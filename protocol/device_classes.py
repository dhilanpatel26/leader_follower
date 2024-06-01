import random
import time
from message_classes import Message, Action


class Device:
    """ Lightweight device object for storing in a DeviceList. """

    def __init__(self, id):  # id will be generated by ThisDevice before attendance response
        """
        Non-default constructor for Device object.
        :param id: specified identifier for instance.
        """
        self.id = id  # unique device identifier, randomly generated
        self.leader = False  # initialized as follower
        self.received = None  # holds most recent message payload
        self.missed = 0  # number of missed check-ins, used by current leader
        self.task = -1  # task identifier, -1 denotes reserve

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
        self.leader = True  # start ThisDevice as leader then change accordingly in setup
        self.device_list = DeviceList()  # default sizing
        self.leader_id = None
        self.leader_started_operating = None
        self.task_folder_idx = None  # multiple operations can be preloaded
        self.received = None  # will be an int representation of message
        self.transceiver = transceiver  # plugin object for sending and receiving messages

    def send(self, action, payload, option, leader_id, follower_id):
        msg = Message(action, payload, option, leader_id, follower_id).msg
        self.transceiver.send(msg)  # transceiver only deals with integers

    def receive(self) -> int:  # int representation of the message (Message.msg)
        return self.transceiver.receive()

    def received_action(self):
        return self.received // 1e26

    def received_leader_id(self):
        return self.received % 1e16 // 1e8

    def received_follower_id(self):
        return self.received % 1e8

    def setup(self):
        # TODO: change number once constants defined
        print("Listening for leader, device " + str(self.id))

        end_time = time.time() + 3
        while time.time() < end_time:
            self.received = self.receive()
            if self.received is not None and self.received_action() == Action.ATTENDANCE.value:
                print("Becoming follower, device " + str(self.id))
                self.make_follower()
                self.follower_receive_attendance()
                return  # early exit if follower
            time.sleep(0.25)

        print("Becoming leader, device " + str(self.id))
        self.make_leader()
        self.leader_send_attendance()

    # TODO: Model communication channel first
    # TODO: leader send attendance
    def leader_send_attendance(self):
        # maybe change so message created here?
        # attendance action=1, payload=0, option=0, leader=thisid, follower = 0
        end_time = time.time() + 3
        while time.time() < end_time:
            self.send(Action.ATTENDANCE.value, 0, 0, self.get_id(), 0)
            time.sleep(0.25)

        # TODO: define the send/receive time constants, change this number after
        end_time = time.time() + 2
        new_device = False
        while time.time() < end_time:
            # are we returning received message or boolean?
            # assuming returning message
            self.received = self.receive()
            if self.received is not None:
                if self.received_action() == Action.ATT_RESPONSE.value:
                    # should we assume the device isn't already in list?

                    # should we assign task now or later?
                    self.device_list.add_device(self.received_follower_id(), -1)
                    new_device = True
                else:
                    continue
            time.sleep(0.25)
        
        if new_device:
            self.leader_send_device_list()

    # TODO: leader send device list
    def leader_send_device_list(self):
        pass

    # TODO: leader send check in
    def leader_send_check_in(self):
        pass

    # TODO: leader send delete
    def leader_send_delete(self):
        pass

    # TODO: leader send task start
    def leader_send_task_start(self):
        pass

    # TODO: leader send task stop
    def leader_send_task_stop(self):
        pass

    # TODO: follower receive attendance
    def follower_receive_attendance(self):
        while self.received_action() != Action.ATTENDANCE.value:
            # could get stuck here - potential error case
            received_msg = self.receive()
        self.leader_id = self.received_leader_id()

        # send response
        self.send(Action.ATT_RESPONSE.value, 0, 0, self.leader_id, self.id)

    # TODO: follower receive device list
    def follower_receive_device_list(self):
        pass

    # TODO: follower receive check in
    def follower_receive_check_in(self):
        pass

    # TODO: follower receive delete
    def follower_receive_delete(self):
        pass

    # TODO: follower receive task start
    def follower_receive_task_start(self):
        pass

    # TODO: follower receive task stop
    def follower_receive_task_stop(self):
        pass

    def handle_promotion(self):
        pass

    # TODO: add edge case takeover situations after

    # TODO: change print to individual files
    def device_main(self):
        print("Starting main on device " + str(self.id))
        # create device object
        self.setup()

        if self.get_leader():
            print("--------Leader---------")
        else:
            print("--------Follower, listening...--------")

        # global looping
        while True:
            print("This is device " + str(self.id))
            print(self.device_list)

            if self.get_leader():  # Leader loop
                # send check in messages and wait for responses
                self.leader_send_check_in()
                # send delete message if response not heard from device after threshold (handled in leader_check_in)

                # send attendance message
                self.leader_send_attendance()
                # listen for new followers
                # send revised list if new followers are heard (handled in leader_send_attendance)

            if not self.get_leader():  # follower loop
                # listen for message
                # handle depending on action code

                if self.receive():
                    action = self.received_action()

                    if self.received_leader_id() != self.leader_id:
                        # device.leader_address = max(device.received.leader_addr, device.leader_address)
                        continue

                    # messages for all followers
                    if action == Action.DELETE.value:
                        reserve_promotion = self.follower_receive_delete()
                        if reserve_promotion is not None:
                            self.task = reserve_promotion

                    elif action == Action.D_LIST.value:
                        print("Updating list on follower side***")
                        self.follower_receive_device_list()

                    elif (
                            action == Action.ATTENDANCE.value
                    ) and self.task is None:  # meaning follower was wrongly deleted
                        self.follower_receive_attendance()

                    elif action == Action.TASK_STOP.value:
                        continue

                    elif action == Action.TASK_START.value:
                        continue

                else:  # no message heard, start takeover protocol
                    print("Is there anybody out there?")

                    if len(self.device_list) == 0:
                        break

                    # Leader dropped out
                    if self.handle_promotion():
                        print("--------Taking over as new leader--------")
                    else:
                        print("Staying as follower under a new leader")


class DeviceList:
    """ Container for lightweight Device objects, held by ThisDevice. """

    def __init__(self, num_tasks=8):
        """
        Non-default constructor for DeviceList object.
        :param num_tasks: size of DeviceList, number of tasks.
        """
        self.devices = []
        self.task_options = list(range(num_tasks))

    def __str__(self):
        """
        String representation of Devices in DeviceList.
        :return: concatenated string representation.
        """

        output = ["DeviceList:"]
        for device in self.devices:
            task = device.get_task() if device.get_task() != -1 else "Reserve"
            output.append(f"Device ID: {hex(device.get_id())}, Task: {task}")
        return "\n\t".join(output)

    def __iter__(self):
        """
        Iterator for Devices in DeviceList.
        :return: iterator object.
        """
        return iter(self.devices)

    def __len__(self):
        """
        Length of Devices in DeviceList.
        :return: number of Devices in DeviceList as an int.
        """
        return len(self.devices)

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
        self.devices.append(device)

    def find_device(self, id: int) -> int or None:
        """
        Finds Device object with target id in DeviceList.
        :param id: identifier for target device.
        :return: Device object if found, None otherwise.
        """
        for device in self.devices:
            if device.get_id() == id:
                return device
        return None

    def remove_device(self, id: int) -> bool:
        """
        Removes Device object with target id in DeviceList.
        :param id: identifier for target device
        :return: True if found and removed, False otherwise.
        """

        device = self.find_device(id)
        if device:
            self.devices.remove(device)
            return True
        return False

    def unused_tasks(self) -> list[int]:
        """
        Gets list of tasks not currently assigned to a device.
        :return: list of unused task indices.
        """
        unused_tasks = self.task_options.copy()
        for d in self.devices:
            if d.get_task() != -1 and d.get_task() in unused_tasks:
                unused_tasks.remove(d.get_task())
        return unused_tasks

    def get_reserves(self):
        """
        Gets list of reserve devices (not currently assigned a task).
        :return: list of reserve devices.
        """
        reserves = []
        for d in self.devices:
            if d.get_task() == -1:
                reserves.append(d)
        return reserves

    def update_task(self, id: int, task: int):
        """
        Reassigns task to target device.
        :param id: identifier for target device.
        :param task: new task to be assigned to target.
        """
        for device in self.devices:
            if device.get_id() == id:
                device.set_task(task)  # pass-by-reference enhanced for allows this?
        # TODO: Exceptions

    def get_highest_id(self) -> Device:
        """
        Gets Device with the largest id, used for leader takeover and tiebreaker.
        :return: Device object with the largest id
        """
        max_device = None
        max_id = 0
        for device in self.devices:
            if device.get_id() > max_id:
                max_id = device.get_id()
                max_device = device  # reference to max Device object
        return max_device

