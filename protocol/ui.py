import os
import time
from message_classes import Message, Action
from abstract_network import AbstractTransceiver
from typing import Any, Dict, List, Set
from pathlib import Path
import csv
from device_classes import ThisDevice, Device, TAKEOVER_DURATION
from enum import Enum
import websockets


class Status(Enum):
    DEAD = 0
    LEADER = 1
    FOLLOWER = 2


class UserInterface(ThisDevice):
    """ Contains backend logic for user interface """

    def __init__(self, transceiver: AbstractTransceiver):
        super().__init__(transceiver=transceiver)
        self.devices: Dict[int, int] = {}

    def flag_new_device():
        pass

    def main(self):
        while True:
            self.receive(duration=TAKEOVER_DURATION)
            action = self.received_action()

            match action:
                case Action.ON.value:  # no fall through
                    follower_id = self.received_follower_id()
                    if follower_id not in self.device_list:
                        self.flag_new_device(follower_id)
                    self.devices[follower_id] = Status.FOLLOWER.value
                    break
                case Action.NEW_FOLLOWER.value:
                    follower_id = self.received_follower_id()
                    if follower_id not in self.device_list:
                        self.flag_new_device(follower_id)
                    self.devices[follower_id] = Status.FOLLOWER.value
                    break
                case Action.OFF.value:  # always sent in follower_id
                    follower_id = self.received_follower_id()
                    if leader_id not in self.devices:
                        self.flag_new_device(leader_id)
                    self.devices[leader_id] = Status.DEAD.value
                case Action.NEW_LEADER.value:
                    leader_id = self.received_leader_id()
                    if leader_id not in self.devices:
                        self.flag_new_device(leader_id)
                    self.devices[leader_id] = Status.LEADER.value
                    break
                case _:
                    pass

    
    # websocket client to connect to server.js and interact with injections
    async def websocket_client(self):
        uri = "ws://localhost:3000"  # server.js websocket server
        async with websockets.connect(uri) as websocket:
            await websocket.send(f"CONNECTED,{self.parent.node_id}")  # initial connection message

            async for message in websocket:
                if isinstance(message, bytes):
                    message = message.decode("utf-8")
                print(f"Received message: {message}")
                if message == "Toggle Device":
                    print("Toggling device")
                    if self.active_status() == 0:  # been off
                        self.reactivate()  # goes through process to full activation
                        await websocket.send(f"REACTIVATED,{self.parent.node_id}")  # reactivation
                    else:
                        self.deactivate()  # recently just turned on
                        await websocket.send(f"DEACTIVATED,{self.parent.node_id}")  # deactivation

    # called via asyncio from a synchronous environment - send, receive
    async def notify_server(self, message: str):
        uri = "ws://localhost:3000"  # server.js websocket server
        async with websockets.connect(uri) as websocket:
            await websocket.send(message)
    
            