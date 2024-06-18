import unittest
import queue
import sys
sys.path.append('../protocol')
from network_classes import Transceiver, SharedQueueList

class TestTransceiver(unittest.TestCase):

    def setUp(self):

        self.channels = SharedQueueList()
        # nodeid=1
        self.transceiver1 = Transceiver(1, self.channels)
        # nodeid=2
        self.transceiver2 = Transceiver(2, self.channels)

        self.q1 = queue.Queue() # for node 1
        self.q2 = queue.Queue() # for node 2

        self.channels.add_channel(1, self.q1)
        self.channels.add_channel(2, self.q2)

    def testSendWithTwoDevices(self):
        # send via transceiver 1
        test1 = 1234
        self.transceiver1.send(test1)
        # check message is received in queue2
        result1 = self.q2.get()
        self.assertEqual(result1, test1)

        test2 = 4321
        self.transceiver2.send(test2)
        result2 = self.q1.get()
        self.assertEqual(result2, test2)

    def testSendWithMultipleDevices(self):
        # nodeid=3
        self.transceiver3 = Transceiver(3, self.channels)

        self.q3 = queue.Queue() # for node 3

        self.channels.add_channel(3, self.q3)

        test1 = 5678
        self.transceiver1.send(test1)
        # not sending to itself
        self.assertTrue(self.q1.empty())
        result_t2 = self.q2.get()
        result_t3 = self.q3.get()
        # both receive correct message
        self.assertEqual(result_t2, test1, "t2 failed")
        self.assertEqual(result_t3, test1, "t3 failed")
        # all are empty after
        self.assertTrue(self.q1.empty())
        self.assertTrue(self.q2.empty())
        self.assertTrue(self.q3.empty())
    
    def testReceiveTwoDevices(self):
        # no dependence on send
        test1 = 8765
        self.q2.put(test1)
        result1 = self.transceiver2.receive(None)
        self.assertEqual(result1, test1)
        self.assertTrue(self.q2.empty())

        # test with send
        test2 = 3210
        self.transceiver1.send(test2)
        self.assertFalse(self.q2.empty())
        result2 = self.transceiver2.receive(None)
        self.assertEqual(result2, test2)
        self.assertTrue(self.q2.empty())



if __name__ == '__main__':
    unittest.main()

