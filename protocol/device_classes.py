import time
from message_classes import Message, Action
from typing import Dict, List, Set
#from network_classes import Transceiver
#this import causes circular w network classes


MISSED_THRESHOLD = 3
RESPONSE_ALLOWANCE = 1  # subject to change


class Device:
    """ Lightweight device object for storing in a DeviceList. """

    def __init__(self, id):  # id will be generated by ThisDevice before attendance response
        """
        Non-default constructor for Device object.
        :param id: specified identifier for instance.
        """
        self.id: int = id  # unique device identifier, randomly generated
        self.leader: bool = False  # initialized as follower
        self.received: int | None = None  # holds most recent message payload
        self.missed: int = 0  # number of missed check-ins, used by current leader
        self.task: int = 0  # task identifier, 0 denotes reserve

    def get_id(self) -> int:
        """
        :return: Device's identifier.
        """
        return self.id

    def get_leader(self) -> bool:
        """
        :return: Device's current leader status.
        """
        return self.leader

    def get_received(self) -> int:
        """
        :return: Device's most recently received message.
        """
        return self.received

    def get_missed(self) -> int:
        """
        :return: number of missed check-ins for this Device.
        """
        return self.missed

    def get_task(self) -> int:
        """
        :return: device's current task identifier
        """
        return self.task

    def make_leader(self):
        """
        Makes this Device a leader
        """
        self.leader = True

    def make_follower(self):
        """
        Makes this Device a follower
        """
        self.leader = False

    def incr_missed(self) -> int:
        """
        Increments number of missed check-ins by 1.
        :return: new number of missed check-ins.
        """
        self.missed += 1
        return self.missed

    def set_task(self, task: int):
        """
        Sets the task for this Device.
        :param task: task's int identifier
        """
        self.task = task


class ThisDevice(Device):
    """ Object for main protocol to use, subclass of Device. """

    def __init__(self, id, transceiver):  # inclusive bounds
        """
        Constructor (default/non-default) for ThisDevice, creates additional fields.
        :param id: identifier for ThisDevice, either pre-specified or randomly generated.
        """
        super().__init__(id)
        self.leader: bool = True  # start ThisDevice as leader then change accordingly in setup
        self.device_list: DeviceList = DeviceList()  # default sizing
        self.leader_id: int | None = None
        self.leader_started_operating: float | None = None
        self.task_folder_idx: int | None = None  # multiple operations can be preloaded
        self.received: int | None = None  # will be an int representation of message
        self.transceiver = transceiver  # plugin object for sending and receiving messages

    def send(self, action, payload, leader_id, follower_id, duration=0.0):
        msg = Message(action, payload, leader_id, follower_id).msg
        print("Message", msg)
        end_time = time.time() + duration
        while time.time() < end_time:
            self.transceiver.send(msg)  # transceiver only deals with integers
            # print("Sending", msg)
            time.sleep(0.2)

    def receive(self, duration, action_value=-1) -> bool:  # action_value=-1 means accepts any action
        # must have low timeout and larger duration so we don't get hung up on a channel
        end_time = time.time() + duration
        while time.time() < end_time:
            self.received = self.transceiver.receive(timeout=0.2)
            # print("Received", self.received)
            if self.received and (action_value == -1 or self.received_action() == action_value):
                return True
        return False

    def received_action(self) -> int:
        return self.received // int(1e24)

    def received_leader_id(self) -> int:
        return self.received % int(1e16) // int(1e8)

    def received_follower_id(self) -> int:
        return self.received % int(1e8)

    def received_payload(self) -> int:
        return self.received % int(1e24) // int(1e16)

    def setup(self):
        print("Listening for leader's attendance")
        if self.receive(duration=3):
            print("Heard someone, listening for attendance")
            while self.received_action() != Action.ATTENDANCE.value:
                self.receive(duration=3)
            self.make_follower()
            self.follower_handle_attendance()
            print("Leader heard, becoming follower")
            return  # early exit if follower

        print("Assuming position of leader")
        self.make_leader()
        self.device_list.add_device(id=self.id, task=1)  # put itself in devicelist with first task
        self.leader_send_attendance()

    def leader_send_attendance(self):
        self.send(action=Action.ATTENDANCE.value, payload=0, leader_id=self.id, follower_id=0, duration=1)

        new_devices = 0
        while self.receive(duration=2, action_value=Action.ATT_RESPONSE.value):
            if self.received_follower_id() not in self.device_list.get_ids():
                self.device_list.add_device(id=self.received_follower_id(), task=0)  # has not assigned task yet
                new_devices += 1

        if new_devices:
            time.sleep(2*new_devices)  # waiting for followers to finish attendance response
            self.leader_send_device_list()

    def leader_send_device_list(self):
        for id, device in self.device_list.get_device_list().items():
            # not using option since DeviceList.devices is a dictionary
            # simply sending all id's in its "list" in follower_id position
            print("Leader sending D_LIST", id, device.task)
            self.send(action=Action.D_LIST.value, payload=device.task, leader_id=self.id, follower_id=id, duration=1)
            time.sleep(1)

    def leader_perform_check_in(self):
        print("Leader performing check-in")
        # leader should listen for check-in response before moving on to ensure scalability
        for id, device in self.device_list.get_device_list().items():
            got_response: bool = False
            # sending check-in to individual device
            self.send(action=Action.CHECK_IN.value, payload=0, leader_id=self.id, follower_id=id, duration=1)
            # device hangs in send() until finished sending
            end_time = time.time() + RESPONSE_ALLOWANCE
            # accounts for leader receiving another device's check-in response (which should never happen)
            while time.time() < end_time:  # times should line up with receive duration
                if self.receive(duration=RESPONSE_ALLOWANCE, action_value=Action.CHECK_IN.value):
                    if self.received_follower_id() == id:
                        # early exit if heard
                        got_response = True
                        print("Leader heard check-in response from", id)
                        break
            if not got_response:
                device.incr_missed()

    def leader_drop_disconnected(self):
        for id, device in self.device_list.get_device_list().items():
            if device.get_missed() > MISSED_THRESHOLD:
                # sends a message for each disconnected device
                self.send(action=Action.DELETE.value, payload=0, leader_id=self.id, follower_id=id, duration=1)
                # broadcasts to entire channel, does not need a response confirmation

    def follower_handle_attendance(self):
        """
        Called after follower has received attendance message and assigned to self.received.
        :return:
        """
        self.leader_id = self.received_leader_id()
        if self.leader_id not in self.device_list.get_ids():
            self.send(action=Action.ATT_RESPONSE.value, payload=0, leader_id=self.leader_id, follower_id=self.id, duration=2)

    def follower_handle_dlist(self):
        print("Follower handling D_LIST")
        while self.receive(duration=1.5, action_value=Action.D_LIST.value):  # while still receiving D_LIST
            self.device_list.add_device(id=self.received_follower_id(), task=self.received_payload())

    # TODO: print log to individual files
    def device_main(self):
        print("Starting main on device " + str(self.id))
        # create device object
        self.setup()

        if self.get_leader():
            print("--------Leader---------")
        else:
            print("--------Follower, listening--------")

        # global looping
        while True:
            print("Device:", self.id, self.leader, "\n", self.device_list)

            if self.get_leader():
                self.leader_send_attendance()  # device_list sending happens here
                time.sleep(1)  # optional, to give followers a chance to finish responding
                # will be helpful if leader works through followers in
                # same order each time to increase clock speed
                self.leader_perform_check_in()  # takes care of sending and receiving
                self.leader_drop_disconnected()

            if not self.get_leader():
                if not self.receive(duration=8):
                    print("Is there anybody out there?")
                    # takeover
                elif abs(self.received_leader_id() - self.leader_id) > 5:  # account for loss of precision
                    # print(self.received_leader_id())
                    # print(self.leader_id)
                    # print("CONTINUE")
                    continue

                action = self.received_action()
                # print(action)

                # messages for all followers
                match action:
                    case Action.DELETE.value:
                        pass
                    case Action.D_LIST.value:
                        self.follower_handle_dlist()
                    case Action.ATTENDANCE.value:
                        pass
                    case Action.TASK_STOP.value:
                        pass
                    case Action.TASK_START.value:
                        pass
                    case _:
                        print("Unknown action")


class DeviceList:
    """ Container for lightweight Device objects, held by ThisDevice. """

    def __init__(self, num_tasks=8):
        """
        Non-default constructor for DeviceList object.
        :param num_tasks: size of DeviceList, number of tasks.
        """
        self.devices = {}  # hashmap of id: Device object
        self.task_options = list(range(num_tasks))

    def __str__(self):
        """
        String representation of Devices in DeviceList.
        :return: concatenated string representation.
        """

        output = ["DeviceList:"]
        for id, device in self.devices.items():
            task = device.get_task() if device.get_task() != 0 else "Reserve"
            output.append(f"Device ID: {id}, Task: {task}")
        return "\n\t".join(output)

    def __iter__(self):
        """
        Iterator for Devices in DeviceList.
        :return: iterator object.
        """
        return iter(self.devices.items())  # dictionary iterator

    def __len__(self):
        """
        Length of Devices in DeviceList.
        :return: number of Devices in DeviceList as an int.
        """
        return len(self.devices)

    def get_device_list(self) -> Dict[int, Device]:
        return self.devices

    def get_ids(self) -> Set[int]:
        return set(self.devices.keys())  # hashtable

    def get_devices(self) -> Set[Device]:
        return set(self.devices.values())  # hashtable

    def update_num_tasks(self, num_tasks: int):
        """
        Resize DeviceList, used to upscale or downscale tasks.
        :param num_tasks: number of tasks in new operation.
        """
        self.task_options = list(range(num_tasks))

    def add_device(self, id: int, task: int):
        """
        Creates Device object with id and task, stores in DeviceList.
        :param id: identifier for device, assigned to new Device object.
        :param task: task for device, assigned to new Device object.
        """
        device = Device(id)
        device.set_task(task)
        self.devices[id] = device

    def find_device(self, id: int) -> int or None:
        """
        Finds Device object with target id in DeviceList.
        :param id: identifier for target device.
        :return: Device object if found, None otherwise.
        """
        return self.devices[id] if id in self.devices.keys() else None

    def remove_device(self, id: int) -> bool:
        """
        Removes Device object with target id in DeviceList.
        :param id: identifier for target device
        :return: True if found and removed, False otherwise.
        """
        try:
            self.devices.pop(id)
            return True
        except KeyError:
            return False

    def unused_tasks(self) -> Set[int]:
        """
        Gets list of tasks not currently assigned to a device.
        :return: list of unused task indices.
        """
        unused_tasks = self.task_options.copy()
        for d in self.devices.values():
            if d.get_task() != 0 and d.get_task() in unused_tasks:
                unused_tasks.remove(d.get_task())
        return set(unused_tasks)  # hashtable

    def get_reserves(self) -> List[Device]:
        """
        Gets list of reserve devices (not currently assigned a task).
        :return: list of reserve devices.
        """
        reserves = []
        for d in self.devices:
            if d.get_task() == 0:
                reserves.append(d)
        return reserves

    def update_task(self, id: int, task: int):
        """
        Reassigns task to target device.
        :param id: identifier for target device.
        :param task: new task to be assigned to target.
        """
        self.devices[id].set_task(task)

    def get_highest_id(self) -> Device | None:
        """
        Gets Device with the largest id, used for leader takeover and tiebreaker.
        :return: Device object with the largest id
        """
        return self.devices[max(self.devices.keys())] if len(self.devices) > 0 else None

