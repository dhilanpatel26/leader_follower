#!/usr/bin/python3
# coding=utf8
import sys
import time
import os
import cv2
import apriltag
import random

sys.path.append('/home/pi/TurboPi/')
import Camera
import HiwonderSDK.Board as Board
import HiwonderSDK.mecanum as mecanum

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

class MainQuadrantMovementFixedSelection:
    def __init__(self):
        self.car = mecanum.MecanumChassis()
        self.camera = Camera.Camera()
        try:
            self.camera.camera_open(correction=True)
        except Exception as e:
            print(f"Error opening camera: {e}")
            sys.exit(1)
        
        self.detector = apriltag.Detector()
        self.running = True
        self.detected_tag_after_turn = None
        self.last_detected_tag = 0
        self.mapSelection = [1, 2, 3]
        self.map1dist = 1
        self.map2dist = 13
        self.map3dist = 20
        self.current_distance = 0

        self.fullIterations = 1

    def move_straight(self, distance_inches):
        duration = distance_inches * 0.13 
        self.car.set_velocity(35, 90, 0)
        time.sleep(duration)
        self.car.set_velocity(0, 90, 0) 

    def move_straight_reverse(self, distance_inches):
        duration = distance_inches * 0.13 
        self.car.set_velocity(-35, 90, 0)
        time.sleep(duration)
        self.car.set_velocity(0, 90, 0) 

    def turn_right(self):
        self.car.set_velocity(0, 90, 0.55) 
        time.sleep(0.55) 
        self.car.set_velocity(0, 90, 0)

    def turn_left(self):
        self.car.set_velocity(0, 90, -0.52)  
        time.sleep(0.55)  
        self.car.set_velocity(0, 90, 0)  

    def handle_last_tag(self):
        if self.last_detected_tag == 0:
            self.turn_right()
        elif self.last_detected_tag == 1:
            self.turn_right()
        elif self.last_detected_tag == 2:
            self.turn_right()
            time.sleep(0.5)
            self.turn_right()
        elif self.last_detected_tag == 3:
            self.turn_left()

    # working version
    def align_with_tag(self, tag):
        aligned = False
        while self.running and not aligned:
            img = self.camera.frame
            if img is None or img.size == 0:
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            tags = self.detector.detect(gray)

            for detected_tag in tags:
                if detected_tag.tag_id == tag:
                    # calculates misalignment (offset) from center
                    tag_center_x = detected_tag.center[0]
                    print("Tag Center X: " + str(tag_center_x))
                    frame_center_x = img.shape[1] / 2
                    print("Frame Center X: " + str(frame_center_x))
                    offset = tag_center_x - frame_center_x

                    if abs(offset) > 40:  # tolerance threshold
                        if offset > 0:
                            self.car.set_velocity(0, 90, 0.30)
                            print("Offset: " + str(offset))
                            time.sleep(0.1)
                        else:
                            self.car.set_velocity(0, 90, -0.30)
                            time.sleep(0.1)

                        # Stop for 0.5 seconds for recalibration
                        self.car.set_velocity(0, 90, 0)
                        print("Waiting for re-calibration")
                        time.sleep(0.5)
                    else:
                        aligned = True
                        self.car.set_velocity(0, 90, 0)
                        time.sleep(0.2)
                        print("Completed Tag Alignment!")
                        break

        return aligned

    def run(self):
        try:
            for i in range(self.fullIterations):
                for map in range(len(self.mapSelection)):
                    current_tag = self.mapSelection[map]

                    self.handle_last_tag()
                    time.sleep(5)

                    if current_tag == 1:
                        self.current_distance = self.map1dist
                    elif current_tag == 2:
                        self.current_distance = self.map2dist
                    elif current_tag == 3:
                        self.current_distance = self.map3dist

                    self.move_straight(self.current_distance)
                    time.sleep(0.5)

                    self.turn_left()
                    time.sleep(1)

                    if self.align_with_tag(current_tag):
                        self.move_straight_reverse(self.current_distance)
                        time.sleep(0.5)

                        if current_tag == 1:
                            self.turn_left()
                        elif current_tag == 2:
                            self.turn_left()
                            time.sleep(0.2)
                            self.turn_left()
                        else:
                            self.turn_right()

                        print("Task Completed!")
                        time.sleep(5)

        except KeyboardInterrupt:
            self.running = False
        finally:
            self.camera.camera_close()
            cv2.destroyAllWindows()

if __name__ == '__main__':
    tester = MainQuadrantMovementFixedSelection()
    tester.run()