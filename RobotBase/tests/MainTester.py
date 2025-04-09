#!/usr/bin/python3
# coding=utf8
import sys
import threading
import time
import os
import cv2
import apriltag

sys.path.append('/home/pi/TurboPi/')
import Camera
import HiwonderSDK.Board as Board
import HiwonderSDK.mecanum as mecanum
import HiwonderSDK.FourInfrared as infrared

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(os.path.join(current_dir, 'functionality_classes'))

from functionality_classes.LineFollowing import LineFollowing
from functionality_classes.AprilTag import AprilTagSensor

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

class MainTester:
    def __init__(self):
        self.car = mecanum.MecanumChassis()
        self.camera = Camera.Camera()
        self.camera.camera_open(correction=True)
        self.detector = apriltag.Detector()
        self.lf_event = threading.Event()
        self.running = True
        self.line_follower = LineFollowing()
        self.line_follower.init()
        self.line_follower.start()

    def run(self):
        try:
            while self.running:
                img = self.camera.frame
                if img is None or img.size == 0:
                    continue

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                tags = self.detector.detect(gray)

                for tag in tags:
                    tag_id = tag.tag_id
                    if tag_id == 4:
                        print("Tag 4 detected. Setting turn flag.")
                        self.line_follower.set_turn_flag(True)  # Set turn flag to True
                        time.sleep(1)  # Duration for the turn
                        self.line_follower.set_turn_flag(False)  # Reset turn flag
                        break  # Exit the loop after detecting tag 4
        except KeyboardInterrupt:
            print("Program interrupted. Stopping line follower.")
            self.running = False
        finally:
            self.camera.camera_close()
            cv2.destroyAllWindows()
            self.line_follower.exit()  # Ensure line follower is properly stopped

if __name__ == '__main__':
    tester = MainTester()
    tester.run()