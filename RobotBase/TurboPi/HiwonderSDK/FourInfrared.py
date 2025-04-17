#!/usr/bin/python3
# coding=utf8
import time
import smbus
import numpy

#四路巡线传感器使用例程 Four-channel line follower routine

class FourInfrared:

    def __init__(self, address=0x78, bus=1):
        self.address = address
        self.bus = smbus.SMBus(bus)

    def readData(self, register=0x01):
        value = self.bus.read_byte_data(self.address, register)
        return [True if value & v > 0 else False for v in [0x01, 0x02, 0x04, 0x08]]
              

if __name__ == "__main__":
    line = FourInfrared()
    while True:
        data = line.readData()
        #True表示识别到黑线，False表示没有识别到黑线 "True" means the black line is recognized, "False" means the black line is not recognized.
        print("Sensor1:", data[0], " Sensor2:", data[1], " Sensor3:", data[2], " Sensor4:", data[3])
        time.sleep(0.5)


