import unittest
from time import sleep
from signal import SIGTERM
import multiprocessing as mp
import sys
sys.path.append('../protocol')
from network_classes import Node, SharedQueueList, Network

class TestNetwork(unittest.TestCase):
    pass