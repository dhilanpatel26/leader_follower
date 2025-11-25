import sys
import threading
import time
import signal
import os

from inference_sdk import InferenceHTTPClient


#result = CLIENT.infer(your_image.jpg, model_id='human-vs-animal/1')

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

from RobotBase.TurboPi.Camera import Camera

sys.path.append('/home/pi/TurboPi')
import HiwonderSDK.mecanum as mecanum

#from RobotBase.TurboPi.ColorSensor import ColorSensor

sys.path.append(os.path.join(current_dir, 'functionality_classes'))

from LineFollowing import LineFollowing
from UltrasonicSensor import Sonar



def ultrasonic_sensor():
    # This method will begin running the ultrasonic sensor
    # and output the distance the ultrasonic sensor is measuring
    # every second (TODO: logic for stopping and detecting other robots)
    s = Sonar()
    s.startSymphony()
    while True:
        time.sleep(1)
        distance = s.getDistance()
        print(distance)

def line_following():
    lf = LineFollowing()
    lf.start()
    signal.signal(signal.SIGINT, lf.manual_stop)
    while lf.__isRunning:
        time.sleep(0.01)

def color_sensor():
    # This method starts running the color sensor which searches for
    # and detects red, green, or blue. Outputs color to CMD
   # cs = ColorSensor()
   # cs.init()
  #  cs.start()
    CLIENT = InferenceHTTPClient(
        api_url = 'https://serverless.roboflow.com',
        api_key = 'uNSO0iqdJyvRElDeJg21'
    )
    camera = Camera()
    camera.camera_open(correction=True)
    while True:
        img = camera.frame
        if img is not None:
            
            frame = img.copy()
            result = CLIENT.infer(frame, model_id='human-vs-animal/1')
            print(result)
            handle_result(result)
           # cs.run(frame)
            time.sleep(1)  # Add a delay to control the frame rate and avoid excessive prints
        else:
            time.sleep(0.01)

def handle_result(result):
    predictions = result.get('predictions', [])
    
    if not predictions:
        print("No predictions found.")
        return
    
    detected_class = predictions[0].get('class', None)

    if detected_class == 'sheep':
        # Do something if 'sheep' is detected
        print("Sheep detected!")

    else:
        # Handle other cases
        print(f"Detected class: {detected_class}")
        move_forward(5)

        
def move_forward(distance):
    duration = distance * 0.13
    car.set_velocity(35,90,0)
    time.sleep(duration)
    car.set_velocity(0,90,0)

if __name__ == '__main__':
    #ultrasonic_thread = threading.Thread(target=ultrasonic_sensor)
    #line_following_thread = threading.Thread(target=line_following)
    car = mecanum.MecanumChassis()
    color_sensor_thread = threading.Thread(target=color_sensor)

    #ultrasonic_thread.start()
    #line_following_thread.start()
    color_sensor_thread.start()

    #ultrasonic_thread.join()
    #line_following_thread.join()
    color_sensor_thread.join()