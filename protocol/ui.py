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
import asyncio


class Status(Enum):
    DEAD = 0
    LEADER = 1
    FOLLOWER = 2


class UserInterface(ThisDevice):
    """ Contains backend logic for user interface """

    def __init__(self, transceiver: AbstractTransceiver):
        super().__init__(transceiver=transceiver)
        self.devices: Dict[int, int] = {}

    def flag(self, tag, id):
        asyncio.run(self.notify_server(f"{tag},{id}"))

    def main(self):
        while True:
            self.receive(duration=TAKEOVER_DURATION)
            action = self.received_action()

            match action:
                case Action.ON.value:  # no fall through
                    follower_id = self.received_follower_id()
                    if follower_id not in self.device_list:
                        self.flag("NEW", follower_id)
                    self.devices[follower_id] = Status.FOLLOWER.value
                    self.flag("FOLLOWER", follower_id)
                    break
                case Action.NEW_FOLLOWER.value:
                    follower_id = self.received_follower_id()
                    if follower_id not in self.device_list:
                        self.flag("NEW", follower_id)
                    self.devices[follower_id] = Status.FOLLOWER.value
                    self.flag("FOLLOWER", follower_id)
                    break
                case Action.OFF.value:  # always sent in follower_id
                    follower_id = self.received_follower_id()
                    if follower_id not in self.devices:
                        self.flag("NEW", follower_id)
                    self.devices[follower_id] = Status.DEAD.value
                    self.flag("DEAD", follower_id)
                    break
                case Action.NEW_LEADER.value:
                    leader_id = self.received_leader_id()
                    if leader_id not in self.devices:
                        self.flag("NEW", leader_id)
                    self.devices[leader_id] = Status.LEADER.value
                    self.flag("LEADER", follower_id)
                    break
                case _:
                    pass

    
    # websocket client to connect to server.js and interact with injections
    async def websocket_client(self):
        uri = "ws://localhost:3000"  # server.js websocket server
        async with websockets.connect(uri) as websocket:
            await websocket.send(f"CONNECTED,BACKEND")  # initial connection message

            async for message in websocket:
                if isinstance(message, bytes):
                    message = message.decode("utf-8")
                print(f"Received message: {message}")
                tag, id = message.split()
                if tag == "TOGGLE":
                    device_id = int(id)
                    if self.devices[device_id] == Status.DEAD.value:
                        self.send(action=Action.ACTIVATE.value, payload=0, leader_id=0, follower_id=device_id)
                    else:
                        # always sent in follower id
                        self.send(action=Action.DEACTIVATE.value, payload=0, leader_id=0, follower_id=device_id)


    # called via asyncio from a synchronous environment - send, receive
    async def notify_server(self, message: str):
        uri = "ws://localhost:3000"  # server.js websocket server
        async with websockets.connect(uri) as websocket:
            await websocket.send(message)
    
            