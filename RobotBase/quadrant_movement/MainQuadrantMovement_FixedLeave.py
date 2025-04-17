import os
import sys
import time

sys.path.append('/home/pi/TurboPi/')

import Camera
import HiwonderSDK.Board as Board
from smbus2 import SMBus, i2c_msg

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(os.path.join(current_dir, 'functionality_classes'))

from functionality_classes.PureColorSensor import PureColorSensor

class Sonar:
    __units = {"mm":0, "cm":1}
    __dist_reg = 0

    __RGB_MODE = 2
    __RGB1_R = 3
    __RGB1_G = 4
    __RGB1_B = 5
    __RGB2_R = 6
    __RGB2_G = 7
    __RGB2_B = 8

    __RGB1_R_BREATHING_CYCLE = 9
    __RGB1_G_BREATHING_CYCLE = 10
    __RGB1_B_BREATHING_CYCLE = 11
    __RGB2_R_BREATHING_CYCLE = 12
    __RGB2_G_BREATHING_CYCLE = 13
    __RGB2_B_BREATHING_CYCLE = 14

    def __init__(self):
        self.i2c_addr = 0x77
        self.i2c = 1
        self.Pixels = [0, 0]
        self.RGBMode = 0

    def __getattr(self, attr):
        if attr in self.__units:
            return self.__units[attr]
        if attr == "Distance":
            return self.getDistance()
        else:
            raise AttributeError('Unknown attribute: %s' % attr)

    def setRGBMode(self, mode):
        try:
            with SMBus(self.i2c) as bus:
                bus.write_byte_data(self.i2c_addr, self.__RGB_MODE, mode)
        except BaseException as e:
            print(e)

    def show(self):
        pass

    def numPixels(self):
        return 2

    def setPixelColor(self, index, rgb):
        try:
            if index != 0 and index != 1:
                return 
            start_reg = 3 if index == 0 else 6
            with SMBus(self.i2c) as bus:
                bus.write_byte_data(self.i2c_addr, start_reg, 0xFF & (rgb >> 16))
                bus.write_byte_data(self.i2c_addr, start_reg+1, 0xFF & (rgb >> 8))
                bus.write_byte_data(self.i2c_addr, start_reg+2, 0xFF & rgb)
                self.Pixels[index] = rgb
        except BaseException as e:
            print(e)

    def getPixelColor(self, index):
        if index != 0 and index != 1:
            raise ValueError("Invalid pixel index", index)
        return ((self.Pixels[index] >> 16) & 0xFF,
                (self.Pixels[index] >> 8) & 0xFF,
                self.Pixels[index] & 0xFF)

    def setBreathCycle(self, index, rgb, cycle):
        try:
            if index != 0 and index != 1:
                return
            if rgb < 0 or rgb > 2:
                return
            start_reg = 9 if index == 0 else 12
            cycle = int(cycle / 100)
            with SMBus(self.i2c) as bus:
                bus.write_byte_data(self.i2c_addr, start_reg + rgb, cycle)
        except BaseException as e:
            print(e)

    def startSymphony(self):
        self.setRGBMode(1)
        self.setBreathCycle(1, 0, 2000)
        self.setBreathCycle(1, 1, 3300)
        self.setBreathCycle(1, 2, 4700)
        self.setBreathCycle(2, 0, 4600)
        self.setBreathCycle(2, 1, 2000)
        self.setBreathCycle(2, 2, 3400)

    def getDistance(self):
        dist = 99999
        try:
            with SMBus(self.i2c) as bus:
                msg = i2c_msg.write(self.i2c_addr, [0])
                bus.i2c_rdwr(msg)
                read = i2c_msg.read(self.i2c_addr, 2)
                bus.i2c_rdwr(read)
                dist = int.from_bytes(bytes(list(read)), byteorder='little', signed=False)
                if dist > 5000:
                    dist = 5000
        except BaseException as e:
            print(e)
        return dist

    def setColorBasedOnDistance(self, distance):
        if distance < 100:
            self.setPixelColor(0, Board.PixelColor(255, 0, 0))
            self.setPixelColor(1, Board.PixelColor(255, 0, 0))
            self.show()
            time.sleep(1)
        elif distance < 500:
            self.setPixelColor(0, Board.PixelColor(255, 165, 0))
            self.setPixelColor(1, Board.PixelColor(255, 165, 0))
            self.show()
            time.sleep(1)
        elif distance < 1000:
            self.setPixelColor(0, Board.PixelColor(255, 255, 0))
            self.setPixelColor(1, Board.PixelColor(255, 255, 0))
            self.show()
            time.sleep(1)
        elif distance < 2000:
            self.setPixelColor(0, Board.PixelColor(0, 255, 0))
            self.setPixelColor(1, Board.PixelColor(0, 255, 0))
            self.show()
            time.sleep(1)
        else:
            self.setPixelColor(0, Board.PixelColor(0, 0, 255))
            self.setPixelColor(1, Board.PixelColor(0, 0, 255))
            self.show()
            time.sleep(1)

    def startSequence(self):
        self.setRGBMode(0)
        self.setPixelColor(0, Board.PixelColor(0, 0, 0))
        self.setPixelColor(1, Board.PixelColor(0, 0, 0))
        self.show()
        time.sleep(0.1)

        cs = PureColorSensor()
        cs.init()
        cs.start()
        camera = Camera.Camera()
        camera.camera_open(correction=True)

        while True:
            distance = self.getDistance()
            if distance > 500:
                print("No obstacle within 500 mm, moving forward.")
                img = camera.frame
                if img is not None:
                    frame = img.copy()
                    cs.run(frame)
                    time.sleep(1)
                else:
                    time.sleep(0.01)
            else:
                print(f"Obstacle detected at {distance} mm, stopping.")
                time.sleep(0.1)

if __name__ == '__main__':
    s = Sonar()
    s.startSequence()
    s.startSymphony()
    while True:
        time.sleep(1)
        distance = s.getDistance()
        print(distance)