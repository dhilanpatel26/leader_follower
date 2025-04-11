import time
import json
import asyncio
import threading
import websockets
from device_classes import ThisDevice, Device
from message_classes import Message, Action
from typing import Dict, List, Set

class UIDevice(ThisDevice):
    """
    Special device that only listens to the network and serves as a UI backend.
    It doesn't send messages to other devices, but forwards the data to the UI frontend.
    """
    def __init__(self, id, transceiver):
        super().__init__(id, transceiver)
        self.connected_clients = set()
        self.loop = None
        self.is_ui_device = True  # overwrite
        # Start WebSocket server in a separate thread
        self.ws_thread = threading.Thread(target=self.start_ws_server)
        self.ws_thread.daemon = True
        self.ws_thread.start()
        
    def start_ws_server(self):
        """Start WebSocket server in a separate thread"""
        async def start_server():
            async with websockets.serve(self.ws_handler, "0.0.0.0", 8765):
                print(f"WebSocket server started on port 8765")
                await asyncio.Future()  # Run forever
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loop = loop
            loop.run_until_complete(start_server())
        except Exception as e:
            print(f"WebSocket server error: {e}")
            import traceback
            traceback.print_exc()

    def send_update(self, update_type, data):
        """Helper to send updates via the event loop without await issues"""
        if not self.loop:
            print("Warning: WebSocket event loop not initialized")
            return
            
        try:
            asyncio.run_coroutine_threadsafe(
                self.broadcast_update(update_type, data), 
                self.loop
            )
        except Exception as e:
            print(f"Error scheduling update: {e}")

    async def ws_handler(self, websocket):
        """Handle WebSocket connections from clients"""
        client_address = websocket.remote_address
        print(f"WebSocket client connected from {client_address[0]}:{client_address[1]}")
        self.connected_clients.add(websocket)
        try:
            await websocket.send(json.dumps({
                "type": "initial_state",
                "device_id": self.id,
                "leader_id": self.leader_id,
                "is_leader": False,
                "is_follower": False,
                "is_ui": True,
                "device_list": self.format_device_list()
            }))
            
            async for message in websocket:
                print(f"Received message from client: {message}")
                
                # Process commands from UI
                try:
                    cmd = json.loads(message)
                    
                    if cmd.get('type') == 'deactivate_device':
                        device_id = cmd.get('deviceId')
                        if device_id:
                            try:
                                device_id = int(device_id)
                                self.toggle_device(device_id, activate=False)
                                await websocket.send(json.dumps({
                                    "type": "command_response",
                                    "command": "deactivate_device",
                                    "status": "success",
                                    "message": f"Sent deactivation command to device {device_id}"
                                }))
                            except ValueError:
                                await websocket.send(json.dumps({
                                    "type": "command_response",
                                    "command": "deactivate_device",
                                    "status": "error",
                                    "message": f"Invalid device ID format: {device_id}"
                                }))
                    
                    elif cmd.get('type') == 'reactivate_device':
                        device_id = cmd.get('deviceId')
                        if device_id:
                            try:
                                device_id = int(device_id)
                                self.toggle_device(device_id, activate=True)
                                await websocket.send(json.dumps({
                                    "type": "command_response",
                                    "command": "reactivate_device",
                                    "status": "success",
                                    "message": f"Sent reactivation command to device {device_id}"
                                }))
                            except ValueError:
                                await websocket.send(json.dumps({
                                    "type": "command_response",
                                    "command": "reactivate_device",
                                    "status": "error",
                                    "message": f"Invalid device ID format: {device_id}"
                                }))
                    
                except json.JSONDecodeError:
                    print(f"Received invalid JSON: {message}")

                    
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Client connection closed: {e}")
        finally:
            self.connected_clients.remove(websocket)
            print(f"Client disconnected: {client_address[0]}:{client_address[1]}")

    def toggle_device(self, device_id, activate=False):
        """Toggle device activation state"""
        action_value = Action.ACTIVATE.value if activate else Action.DEACTIVATE.value
        action_name = "activation" if activate else "deactivation"
        
        print(f"Sending {action_name} command to device {device_id}")
        
        # Create message with appropriate action
        msg = Message(action_value, 0, 0, device_id).msg

        is_mock = hasattr(self.transceiver, 'sub_client') and hasattr(self.transceiver.sub_client, '__class__') and \
                self.transceiver.sub_client.__class__.__name__ == 'MockMQTTClient'
                
        if not is_mock:
            self.transceiver.send(msg)
        else:
            print(f"Mock send: {msg}")

        # Log and notify UI clients
        self.send_update("message_log", {
            "type": "send",
            "action": action_value,
            "payload": 0,
            "leader_id": 0,
            "follower_id": device_id,
            "message": f"{action_name.capitalize()} command sent to device {device_id}"
        })
        
        # For mock devices in device_main simulation
        try:
            # Access the mock_devices list if it exists in the current context
            if hasattr(self, 'mock_devices'):
                for i, device in enumerate(self.mock_devices):
                    if device["id"] == device_id:
                        # Set missed count based on activation state (0=active, 3=inactive)
                        self.mock_devices[i]["missed"] = 0 if activate else 3
                        status = "active" if activate else "inactive"
                        print(f"Mock device {device_id} is now {status}")
                        
                        # Update UI
                        self.send_update("device_list", self.mock_devices)
        except Exception as e:
            print(f"Error handling mock device: {e}")

    def format_device_list(self) -> List[Dict]:
        """Format device list for JSON serialization"""
        result = []
        for device_id, device in self.device_list.get_device_list().items():
            result.append({
                "id": device_id,
                "task": device.get_task(),
                "leader": device.get_leader(),
                "missed": device.get_missed()
            })
        return result

    async def broadcast_update(self, update_type, data):
        """Broadcast update to all connected clients"""
        if not self.connected_clients:
            return
            
        message = json.dumps({
            "type": update_type,
            "timestamp": time.time(),
            "data": data
        })
        
        await asyncio.gather(
            *[client.send(message) for client in self.connected_clients]
        )

    # Override methods to prevent sending messages
    def send(self, action: int, payload: int, leader_id: int, follower_id: int, duration: float = 0.0):
        """
        Override send to not actually send to the network
        """
        # Only log the message, don't actually send it
        msg = Message(action, payload, leader_id, follower_id).msg
        
        # Broadcast to UI clients instead
        self.send_update("message_log", {
            "type": "send",
            "action": action,
            "payload": payload,
            "leader_id": leader_id,
            "follower_id": follower_id
        })

    def make_leader(self):
        """Override make_leader to not send any messages"""
        super().make_leader()
        self.send_update("status_change", {"is_leader": True})

    def make_follower(self):
        """Override make_follower to not send any messages"""
        super().make_follower()
        self.send_update("status_change", {"is_leader": False})

    # Override receive to broadcast received messages to UI
    def receive(self, duration, action_value=-1) -> bool:
        """
        Gets first message heard from transceiver with specified action,
        and broadcasts it to connected UI clients.
        """
        # Use the original receive logic
        result = super().receive(duration, action_value)
        
        # If we received a message, broadcast it to UI
        if result and self.received:
            try:
                action = self.received_action()
                leader_id = self.received_leader_id()
                follower_id = self.received_follower_id()
                payload = self.received_payload()
                
                self.send_update("received_message", {
                    "action": action,
                    "leader_id": leader_id,
                    "follower_id": follower_id,
                    "payload": payload,
                    "raw": self.received
                })
                
                # Also broadcast device list updates when appropriate
                if action in [Action.D_LIST.value, Action.DELETE.value]:
                    self.send_update("device_list", self.format_device_list())
                
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                
        return result
    
    # purely for testing without robots
    def device_main(self):
        """Override device_main to avoid requiring real messages"""        
        # Notify connected clients we're online
        self.send_update("status", {"status": "online"})
        
        # Set UI device to always be a follower
        self.leader = None
        self.device_role = "ui"
        
        # Create five mock devices for testing - initially device 1001 is the leader
        self.mock_devices = [
            {"id": 1001, "task": 1, "leader": True, "missed": 0, "role": "leader"},   # Position 1
            {"id": 1002, "task": 2, "leader": False, "missed": 0, "role": "follower"},  # Position 2
            {"id": 1003, "task": 3, "leader": False, "missed": 0, "role": "follower"},  # Position 3
            {"id": 1004, "task": 4, "leader": False, "missed": 0, "role": "follower"},  # Position 4
            {"id": 1005, "task": 5, "leader": False, "missed": 0, "role": "follower"},  # Position 5
        ]

        # ui_device = {"id": self.id, "task": None, "leader": None, "missed": 0, "role": "ui"}
        
        # Set the initial leader ID
        current_leader_idx = 0
        self.leader_id = self.mock_devices[current_leader_idx]["id"]
        
        # For simulating device activities
        positions = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}  # Maps position to device index
        
        # Just keep running - the WebSocket thread handles UI communication
        counter = 0
        try:
            while True:
                # Every 10 seconds, switch leader to another device (never UI device)
                if counter % 10 == 0 and counter > 0:
                    # Make current leader a follower
                    self.mock_devices[current_leader_idx]["leader"] = False
                    
                    # Pick a new leader (cycling through devices 0-4)
                    current_leader_idx = (current_leader_idx + 1) % 5
                    self.mock_devices[current_leader_idx]["leader"] = True
                    self.leader_id = self.mock_devices[current_leader_idx]["id"]
                    
                    # Broadcast leadership change
                    self.send_update("status_change", {
                        "is_leader": False,  # UI device is always follower
                        "leader_id": self.leader_id
                    })
                    print(f"New leader: Device {self.leader_id}")
                    
                    # Simulate leader sending attendance request
                    self.send_update("message_log", {
                        "type": "send",
                        "action": 1,  # ATTENDANCE
                        "payload": counter,
                        "leader_id": self.leader_id,
                        "follower_id": 0  # Broadcast to all
                    })
                
                # Every 15 seconds, move a random device to a new position
                if counter % 15 == 0 and counter > 0:
                    # Pick a random device to move
                    device_idx = counter % 5
                    old_task = self.mock_devices[device_idx]["task"]
                    
                    # Find an empty position or swap with another device
                    new_task = (old_task % 5) + 1
                    
                    # Update position mapping
                    if new_task in positions:
                        other_device_idx = positions[new_task]
                        self.mock_devices[other_device_idx]["task"] = old_task
                        positions[old_task] = other_device_idx
                    
                    # Set new task for moved device
                    self.mock_devices[device_idx]["task"] = new_task
                    positions[new_task] = device_idx
                    
                    # Broadcast task assignment
                    self.send_update("message_log", {
                        "type": "send",
                        "action": 3,  # ASSIGN_TASK
                        "payload": new_task,
                        "leader_id": self.leader_id,
                        "follower_id": self.mock_devices[device_idx]["id"]
                    })
                    print(f"Device {self.mock_devices[device_idx]['id']} moved to position {new_task}")
                
                # Every 8 seconds, simulate a heartbeat/ping
                if counter % 8 == 0:
                    # Leader pings a random follower
                    target_idx = (counter // 8) % 5
                    if target_idx != current_leader_idx:  # Don't ping self
                        self.send_update("message_log", {
                            "type": "send",
                            "action": 5,  # PING
                            "payload": 0,
                            "leader_id": self.leader_id,
                            "follower_id": self.mock_devices[target_idx]["id"]
                        })
                        
                        # Simulate follower response
                        self.send_update("received_message", {
                            "action": 6,  # PONG
                            "leader_id": self.leader_id,
                            "follower_id": self.mock_devices[target_idx]["id"],
                            "payload": 0,
                            "raw": 6000000000000
                        })
                
                # Every 17 seconds, simulate a device going inactive/active
                if counter % 17 == 0 and counter > 0:
                    inactive_idx = counter % 5
                    if inactive_idx != current_leader_idx:  # Don't make leader inactive
                        # Toggle missed count (0 = active, >0 = inactive)
                        self.mock_devices[inactive_idx]["missed"] = 0 if self.mock_devices[inactive_idx]["missed"] > 0 else 2
                        status = "inactive" if self.mock_devices[inactive_idx]["missed"] > 0 else "active"
                        print(f"Device {self.mock_devices[inactive_idx]['id']} is now {status}")
                
                # Every 5 seconds, broadcast updated device list
                if counter % 5 == 0:
                    self.send_update("device_list", self.mock_devices)
                    print("Device list updated")
                
                # Occasionally simulate arbitrary message exchange
                if counter % 23 == 0 and counter > 0:
                    # Random action type for variety
                    action_type = (counter % 7) + 1
                    self.send_update("received_message", {
                        "action": action_type,
                        "leader_id": self.leader_id,
                        "follower_id": self.mock_devices[counter % 5]["id"],
                        "payload": counter,
                        "raw": int(f"{action_type}00{self.leader_id}0{self.mock_devices[counter % 5]['id']}{counter}")
                    })
                
                counter += 1
                time.sleep(1)
        except KeyboardInterrupt:
            print("UI Device shutting down")
