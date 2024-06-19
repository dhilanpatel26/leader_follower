import unittest
from time import sleep, time
from signal import SIGTERM
import multiprocessing as mp
import sys
sys.path.append('../protocol')
from network_classes import Node, SharedQueueList

def test_worker():
    print("child process starting...")
    sleep(1)
    print("child process ending...")
    # send the test child processes here

def test_transmission(transceiver, node_id):
    print("sending transmission")
    transceiver.send(node_id)

def test_send_and_receive(transceiver, node_id):
    print("sending + receiving")
    transceiver.send(node_id)
    sleep(1)
    result = transceiver.receive(2)
    print(result)

def test_leader(transceiver, node_id):
    print("sending as leader")
    transceiver.send(node_id)
    result = transceiver.receive(3)
    print("leader received:", result)

def test_follow(transceiver, node_id):
    result = transceiver.receive(3)
    if result == 1:
        transceiver.send(node_id)

def test_listen(transceiver, node_id):
    start = time()

    result = transceiver.receive(3)
    print("listener received:", result)

    result = transceiver.receive(3)
    print("listener received:", result)


class TestNode(unittest.TestCase):
    def setUp(self):
        self.channels_list = SharedQueueList()
        self.q1 = mp.Queue() # node 1 
        self.q2 = mp.Queue() # node 2 
        self.q3 = mp.Queue()

        self.channels_list.add_channel(1, self.q1)
        self.channels_list.add_channel(2, self.q2)
        self.channels_list.add_channel(3, self.q3)

    # Transceiver unit tests have passed
    def testConstructor(self):
        # test with nodeid of 1, no process function passed
        node1 = Node(1, self.channels_list, test_worker)
        self.assertEqual(node1.node_id, 1)

        # check hash is correct
        hash_val = node1.__hash__() % 10000
        self.assertEqual(node1.thisDevice.id, hash_val)

        # check process created works
        self.assertIsInstance(node1.process, mp.Process)
        node1.process.start()
        self.assertTrue(node1.process.is_alive())
        node1.process.join()
        self.assertFalse(node1.process.is_alive())

    def testProcessStartStop(self):
        node = Node(1, self.channels_list, test_worker)
        node.start()
        self.assertTrue(node.process.is_alive())
        node.stop()
        # small delay because it takes a second for terminate to execute
        sleep(0.1)
        self.assertFalse(node.process.is_alive())
        self.assertEqual(node.process.exitcode, -SIGTERM)

    def testProcessSendBetweenTwoProcesses(self):
        node1 = Node(1, self.channels_list, test_transmission, "not none")
        node2 = Node(2, self.channels_list, test_transmission, "not none")

        node1.start()
        node2.start()

        node1.join()
        node2.join()

        self.assertFalse(self.channels_list.channels[1].empty())
        self.assertFalse(self.channels_list.channels[2].empty())

        result1 = node1.transceiver.receive(2)
        result2 = node2.transceiver.receive(2)

        self.assertEqual(result1, 2)
        self.assertEqual(result2, 1)

    def testProcessReceiveBetweenTwoProcesses(self):
        node1 = Node(1, self.channels_list, test_send_and_receive, "flag")
        node2 = Node(2, self.channels_list, test_send_and_receive, "flag")

        node1.start()
        node2.start()

        node1.join()
        node2.join()

        self.assertTrue(self.channels_list.channels[1].empty())
        self.assertTrue(self.channels_list.channels[2].empty())

    def testProcessSendBetweenMultipleProcesses(self):
        node1 = Node(1, self.channels_list, test_leader, "flag")
        node2 = Node(2, self.channels_list, test_follow, "flag")
        node3 = Node(3, self.channels_list, test_listen, "flag")

        node1.start()
        node2.start()
        node3.start()

        node1.join()
        node2.join()
        node3.join()

        # test three comm lines created and can send individually
        # test can send multiple (for attendance)

if __name__ == '__main__':
    unittest.main()

