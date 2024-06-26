import unittest
import sys
from base_test import PROTOCOL_DIR
sys.path.append(str(PROTOCOL_DIR))
import message_classes as mc

class TestMessageClass(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic_constructor(self):
        # basic test
        basic_msg = mc.Message(1, 0, 0, 0)
        corr_msg = 1e10
        message = "Basic constructor message not equal to 1e10"
        self.assertEqual(basic_msg.msg, corr_msg, message)

    # TODO: test invalid action code - not implemented in message yet
    # useful to have to identify dropped packets
    def test_invalid_action(self):
        pass

    # TODO: test negative options (task assignment = reserve) - not implemented in message yet
    def test_negative_option(self):
        pass


if __name__ == '__main__':
    unittest.main()
    

    

    