import unittest
import sys
from base_test import PROTOCOL_DIR
sys.path.append(str(PROTOCOL_DIR))
import channel_driver as cd

class TestCommunicationChannel(unittest.TestCase):
    def setUp(self):
        pass
        
    # Basic tests with one device
    def testOneDeviceIsLeader(self):
        pass

    def testOneDeviceDeviceList(self):
        pass

    def testOneDeviceAttendanceMessage(self):
        pass

    def testOneDeviceNotSendingCheckIn(self):
        pass

    def testOneDeviceAssignedTaskAndWorking(self):
        pass

    # Basic tests with five devices
    def testFiveDevicesSetup(self):
        # setup channel

        # call all test functions

        pass

    def testFirstDeviceIsLeader(self):
        pass

    def testAllUniqueIds(self):
        pass

    def testAllDeviceLists(self):
        pass

    def testAllWorking(self):
        pass

