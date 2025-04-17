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

class MainQuadrantMovementRandomSelection:
    def __init__(self):
        self.car = mecanum.MecanumChassis()
        self.camera = Camera.Camera()
        self.camera.camera_open(correction=True)
        self.detector = apriltag.Detector()
        self.running = True
        self.detected_tag_after_turn = None
        self.map1dist = 1
        self.map2dist = 13
        self.map3dist = 20
        self.current_distance = 0 

    def move_straight(self, distance_inches):
        duration = distance_inches * 0.13 
        print(f"Moving straight for {distance_inches} inches.")
        self.car.set_velocity(35, 90, 0)
        time.sleep(duration)
        self.car.set_velocity(0, 90, 0) 
        print("Stopped moving straight.")

    def move_straight_reverse(self, distance_inches):
        duration = distance_inches * 0.13 
        print(f"Moving straight for {distance_inches} inches in reverse.")
        self.car.set_velocity(-35, 90, 0)
        time.sleep(duration)
        self.car.set_velocity(0, 90, 0) 
        print("Stopped moving straight in reverse.")

    def turn_right(self):
        print("Turning right.")
        self.car.set_velocity(0, 90, 0.5) 
        time.sleep(0.55) 
        self.car.set_velocity(0, 90, 0)
        print("Completed turning right.")

    def turn_left(self):
        print("Turning left.")
        self.car.set_velocity(0, 90, -0.5)  
        time.sleep(0.55)  
        self.car.set_velocity(0, 90, 0)  
        print("Completed turning left.")

    def run(self):
        try:
            for _ in range(5):
                random_num = random.randint(1, 3)
                print(f"Generated random number: {random_num}")

                self.turn_right()

                time.sleep(1)

                if random_num == 1:
                    self.current_distance = self.map1dist
                elif random_num == 2:
                    self.current_distance = self.map2dist
                elif random_num == 3:
                    self.current_distance = self.map3dist
                else:
                    print("Random number not generated!")
                    self.current_distance = 0

                self.move_straight(self.current_distance)

                time.sleep(0.5)

                self.turn_left()

                time.sleep(1)

                while self.running:
                    img = self.camera.frame
                    if img is None or img.size == 0:
                        print("No image captured. Skipping frame.")
                        continue

                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    tags = self.detector.detect(gray)

                    # Check for any tag detection
                    for tag in tags:
                        tag_id = tag.tag_id
                        if tag_id in [1, 2, 3]:
                            self.detected_tag_after_turn = tag_id
                            print(f"Detected tag: {self.detected_tag_after_turn}")
                            break
                    else:
                        print("No relevant tag detected. Continuing to check...")

                    if self.detected_tag_after_turn is not None:
                        self.turn_right()
                        time.sleep(0.5)
                        self.move_straight_reverse(self.current_distance)
                        time.sleep(0.5)

                        if random_num == 1:
                            self.turn_left()
                        elif random_num == 2:
                            self.turn_left()
                            time.sleep(0.2)
                            self.turn_left()
                        else:
                            self.turn_right()

                        break

                time.sleep(5)

        except KeyboardInterrupt:
            print("Program interrupted.")
            self.running = False
        finally:
            print("Shutting down.")
            self.camera.camera_close()
            cv2.destroyAllWindows()

if __name__ == '__main__':
    tester = MainQuadrantMovementRandomSelection()
    tester.run()