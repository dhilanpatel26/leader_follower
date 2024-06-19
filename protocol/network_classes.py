import device_classes as dc
import multiprocessing
import queue as q


class Node:
    def __init__(self, node_id, shared_queues, target_func=None, target_args=None):
        self.node_id = node_id
        self.transceiver = Transceiver(node_id, shared_queues)
        self.thisDevice = dc.ThisDevice(self.__hash__() % 10000, self.transceiver)
        # for testing purposes, so node can be tested without device protocol fully implemented
        # can be removed later
        if target_func is None:
            target_func = self.thisDevice.device_main
        if target_args is not None:
            target_args = (self.transceiver, self.node_id)
            self.process = multiprocessing.Process(target=target_func, args=target_args)
        else:
            self.process = multiprocessing.Process(target=target_func)

    def start(self):
        self.process.start()

    def stop(self):
        # terminate will kill process so I don't think we need to join after - this can corrupt shared data
        self.process.terminate()
        # self.process.join()

    def join(self):
        # not sure if needed for protocol, but was used during testing
        self.process.join()

class Network:
    def __init__(self):
        self.nodes = {}
        self.channels = SharedQueueList()

    def add_node(self, node_id):
        new_node = Node(node_id, self.channels)
        self.nodes[node_id] = new_node

        new_queue = multiprocessing.Queue()
        self.channels.add_channel(node_id, new_queue)

    def get_node(self, node_id):
        return self.nodes.get(node_id)

# TODO: implement removing channels (node_ids) as devices get dropped from devicelist
# similar implementation to send/receive calling transceiver functions
class Transceiver:
    def __init__(self, node_id, shared_channels):
        self.node_id = node_id
        self.shared_channels = shared_channels

    def send(self, msg: int):  # send to all channels
        self.shared_channels.sendall(self.node_id, msg)

    def receive(self, timeout: float) -> int | None:  # get from all queues
        return self.shared_channels.receive(self.node_id, timeout)
    
class SharedQueueList:
    def __init__(self):
        self.channels = {}

    def add_channel(self, node_id, queue):
        self.channels[node_id] = queue

    def sendall(self, sender, msg):
        for id, channel in self.channels.items():
            if id != sender and channel != None:
                channel.put(msg)

    def receive(self, receiver, timeout):
        channel = self.channels[receiver]
        msg = channel.get(timeout=timeout)
        return msg

