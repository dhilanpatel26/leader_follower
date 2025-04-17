#!/usr/bin/python3
# coding=utf8
import os
import sys
import time
import signal
import threading

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append('/home/pi/TurboPi/')

import HiwonderSDK.Board as Board
import HiwonderSDK.mecanum as mecanum
import HiwonderSDK.FourInfrared as infrared

sys.path.append(os.path.join(current_dir, 'functionality_classes'))

from functionality_classes.ColorSensor import ColorSensor

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

car = mecanum.MecanumChassis()
line = infrared.FourInfrared()
color_sensor = ColorSensor()
__isRunning = False

def initMove():
    car.set_velocity(0, 0, 0)
    print("Initialization complete. Car set to stop.")

def move():
    global __isRunning

    color_sensor.start()  # Initialize and start the color sensor

    time.sleep(2)

    while __isRunning:
        try:
            # Get detected color from ColorSensor
            detect_color = color_sensor.get_detected_color()

            print(f"Detected color: {detect_color}")
            if detect_color == 'green':
                print("Detected green color, turning left")
                car.set_velocity(35, 45, 0)  # Turn left
            else:
                car.set_velocity(35, 90, 0)  # Move forward

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(0.1)

    # Clean up
    color_sensor.stop()

def manual_stop(signum, frame):
    global __isRunning
    __isRunning = False
    car.set_velocity(0, 0, 0)
    color_sensor.stop()

if __name__ == '__main__':
    initMove()
    __isRunning = True
    signal.signal(signal.SIGINT, manual_stop)

    move_thread = threading.Thread(target=move)
    move_thread.setDaemon(True)
    move_thread.start()

    try:
        while __isRunning:
            time.sleep(1)
    except KeyboardInterrupt:
        manual_stop(None, None)
