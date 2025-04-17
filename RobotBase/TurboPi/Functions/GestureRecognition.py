#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/TurboPi/')
import cv2
import time
import math
import signal
import Camera
import threading
import numpy as np
import yaml_handle
import mediapipe as mp
import HiwonderSDK.Board as Board
import HiwonderSDK.mecanum as mecanum

# 手势识别 Gesture Recognition 

car = mecanum.MecanumChassis()
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(model_complexity=0,min_detection_confidence=0.5,min_tracking_confidence=0.5)


if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)


servo1 = 1500
servo2 = 1500

stop_st = False
size = (640, 480)
servo_data = None
gesture_num = None
__isRunning = False
results_lock = False

def load_config():
    global servo_data
    
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)

# 初始位置  Initial Position 
def initMove():
    Board.setPWMServoPulse(1, servo1, 1000)
    Board.setPWMServoPulse(2, servo2, 1000)

# 变量重置 Reset Variables
def reset(): 
    global stop_st, gesture_num
    global servo1,servo2,results_lock
    
    stop_st = False
    gesture_num = None
    results_lock = False
    servo1 = servo_data['servo1'] - 350
    servo2 = servo_data['servo2']

# app初始化调用 APP Initialization
def init():
    print("GestureRecognition Init")
    load_config()
    reset()
    initMove()

# app开始玩法调用 App starts calling game program
def start():
    global __isRunning
    reset()
    __isRunning = True
    print("GestureRecognition Start")

# app停止玩法调用 App stops calling game program 
def stop():
    global stop_st
    global __isRunning
    stop_st = True
    __isRunning = False
    print("GestureRecognition Stop")

# app退出玩法调用 Exit the game
def exit():
    global stop_st
    global __isRunning
    stop_st = True
    __isRunning = False
    print("GestureRecognition Exit")

# 设置蜂鸣器 Set Buzzer
def setBuzzer(timer):
    Board.setBuzzer(0)
    Board.setBuzzer(1)
    time.sleep(timer)
    Board.setBuzzer(0)

# 关闭电机 Turn off motor 
def car_stop():
    car.set_velocity(0,90,0) # 控制机器人移动函数,线速度0(0~100)，方向角90(0~360)，偏航角速度0(-2~2) The movement control function. The linear velocity is 0 (0~100), the direction angle is 90(0~360), and the yaw velocity is 0(-2~2).
# 机器人移动逻辑处理 Movement Processing
def move():
    global __isRunning, stop_st
    global gesture_num, results_lock

    while True:
        if __isRunning:
            if results_lock and gesture_num:
                if gesture_num == 1: # 手势为1，机器人向前移动一段距离  Gesture 1, robot moves forward a certain distance
                    car.set_velocity(45,90,0) # 控制机器人移动函数,线速度45(0~100)，方向角90(0~360)，偏航角速度0(-2~2)  The movement control function. The linear velocity is 0 (0~100), the direction angle is 90(0~360), and the yaw velocity is 0(-2~2).
                    time.sleep(1)
                    car.set_velocity(0,90,0) 
                elif gesture_num == 2: # 手势为2，机器人向后移动一段距离  Gesture 2, robot moves backward a certain distance
                    car.set_velocity(45,270,0)
                    time.sleep(1)
                    car.set_velocity(0,90,0)
                elif gesture_num == 3: # 手势为3，机器人向右移动一段距离  Gesture 3, robot moves a certain distance to the right
                    car.set_velocity(45,270,0)
                    car.set_velocity(45,0,0)
                    time.sleep(1)
                    car.set_velocity(0,90,0)
                elif gesture_num == 4: # 手势为4，机器人向左移动一段距离  Gesture 4, robot moves a certain distance to the left
                    car.set_velocity(45,180,0)
                    time.sleep(1)
                    car.set_velocity(0,90,0)
                elif gesture_num == 5: # 手势为5，机器人顺时针转一圈  Gesture 5, robot turns clockwise once 
                    car.set_velocity(0,90,0.5)
                    time.sleep(2.8)
                    car.set_velocity(0,90,0)
                elif gesture_num == 6: # 手势为6，机器人逆时针转一圈  Gesture 5, robot turns counterclockwise once 
                    car.set_velocity(0,90,-0.5)
                    time.sleep(2.8)
                    car.set_velocity(0,90,0)
                    
                results_lock = False
                
            else:
                if stop_st:
                    initMove()  # 回到初始位置 Return to the initial Position 
                    car_stop() 
                    stop_st = False
                    time.sleep(0.5)               
                time.sleep(0.01)
        else:
            if stop_st:
                initMove()  # 回到初始位置 Return to the initial Position 
                car_stop() 
                stop_st = False
                time.sleep(0.5)               
            time.sleep(0.01)

# 运行子线程 Run child thread
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()


def vector_2d_angle(v1, v2):
    # 求两个向量夹角 calculate the angle bwteen two vectors
    
    v1_x = v1[0]
    v1_y = v1[1]
    v2_x = v2[0]
    v2_y = v2[1]
    try:
        angle_ = math.degrees(math.acos(
            (v1_x * v2_x + v1_y * v2_y) / (((v1_x ** 2 + v1_y ** 2) ** 0.5) * ((v2_x ** 2 + v2_y ** 2) ** 0.5))))
    except:
        angle_ = 65535.0
    if angle_ > 180.0:
        angle_ = 65535.0
    return angle_

def hand_angle(hand_):
    # 获取对应的手指相关向量的角度 Obtain the angle of the related vector of corresponding finger
    
    angle_list = []
    # ---------------------------- thumb
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[2][0])), (int(hand_[0][1]) - int(hand_[2][1]))),
        ((int(hand_[3][0]) - int(hand_[4][0])), (int(hand_[3][1]) - int(hand_[4][1])))
    )
    angle_list.append(angle_)
    # ---------------------------- index
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[6][0])), (int(hand_[0][1]) - int(hand_[6][1]))),
        ((int(hand_[7][0]) - int(hand_[8][0])), (int(hand_[7][1]) - int(hand_[8][1])))
    )
    angle_list.append(angle_)
    # ---------------------------- middle
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[10][0])), (int(hand_[0][1]) - int(hand_[10][1]))),
        ((int(hand_[11][0]) - int(hand_[12][0])), (int(hand_[11][1]) - int(hand_[12][1])))
    )
    angle_list.append(angle_)
    # ---------------------------- ring
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[14][0])), (int(hand_[0][1]) - int(hand_[14][1]))),
        ((int(hand_[15][0]) - int(hand_[16][0])), (int(hand_[15][1]) - int(hand_[16][1])))
    )
    angle_list.append(angle_)
    # ---------------------------- pink
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[18][0])), (int(hand_[0][1]) - int(hand_[18][1]))),
        ((int(hand_[19][0]) - int(hand_[20][0])), (int(hand_[19][1]) - int(hand_[20][1])))
    )
    angle_list.append(angle_)
    return angle_list

def gesture(angle_list):
    # 用手指相关的角度来定义手势 Define gesture according to the finger angle 
    
    gesture_num = 0
    thr_angle = 65.0
    thr_angle_s = 49.0
    thr_angle_thumb = 53.0
    if 65535.0 not in angle_list:
        if (angle_list[0] > 5) and (angle_list[1] < thr_angle_s) and (angle_list[2] > thr_angle) and (
                angle_list[3] > thr_angle) and (angle_list[4] > thr_angle):
            gesture_num = 1
        elif (angle_list[0] > thr_angle_thumb) and (angle_list[1] < thr_angle_s) and (angle_list[2] < thr_angle_s) and (
                angle_list[3] > thr_angle) and (angle_list[4] > thr_angle):
            gesture_num = 2
        elif (angle_list[0] > thr_angle_thumb) and (angle_list[1] < thr_angle_s) and (angle_list[2] < thr_angle_s) and (
                angle_list[3] < thr_angle_s) and (angle_list[4] > thr_angle):
            gesture_num = 3
        elif (angle_list[0] > thr_angle_thumb) and (angle_list[1] < thr_angle_s) and (angle_list[2] < thr_angle_s) and (
                angle_list[3] < thr_angle_s) and (angle_list[4] < thr_angle_s):
            gesture_num = 4
        elif (angle_list[0] < thr_angle_s) and (angle_list[1] < thr_angle_s) and (angle_list[2] < thr_angle_s) and (
                angle_list[3] < thr_angle_s) and (angle_list[4] < thr_angle_s):
            gesture_num = 5
        elif (angle_list[0] < thr_angle_s) and (angle_list[1] > thr_angle) and (angle_list[2] > thr_angle) and (
                angle_list[3] > thr_angle) and (angle_list[4] < thr_angle_s):
            gesture_num = 6

    return gesture_num

# 机器人图像处理  Image processing
results_list = []
def run(img):
    global __isRunning
    global gesture_num
    global results_lock
    global results_list
    
    if not __isRunning:  # 检测是否开启玩法，没有开启则返回原图像  Detect whether the game is started, if not, the orginal image will be returned
        return img
    
    if results_lock: # 上一个动作还在执行,返回原图像 if the previous action is still in operation, the original image is returned.
        return img

    gesture_num = 0
    img_copy = img.copy()
    img_h, img_w = img.shape[:2]
    imgRGB = cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            hand_local = [(landmark.x * img_w, landmark.y * img_h) for landmark in hand_landmarks.landmark]
            if hand_local:
                angle_list = hand_angle(hand_local)
                gesture_results = gesture(angle_list)
                cv2.putText(img, str(gesture_results), (20, 50), 0, 2, (255, 100, 0), 3)
                if gesture_results:
                    results_list.append(gesture_results)
                    if len(results_list) == 5:
                        gesture_num = np.mean(np.array(results_list))
                        results_lock = True
                        results_list = []
    
    return img

# 关闭前处理 Processing before exit
def manual_stop(signum, frame):
    global __isRunning
    
    print('关闭中...')
    __isRunning = False
    car_stop()  # 关闭所有电机 Turn off all motors 
    initMove()  # 舵机回到初始位置 Motor returns to the initial position

if __name__ == '__main__':
    init()
    start()
    camera = Camera.Camera()
    camera.camera_open(correction=True) # 开启畸变矫正,默认不开启 Enable distortion correction which is not enabled by default
    signal.signal(signal.SIGINT, manual_stop)
    while __isRunning:
        img = camera.frame
        if img is not None:
            frame = img.copy()
            Frame = run(frame)  
            frame_resize = cv2.resize(Frame, (320, 240))
            cv2.imshow('frame', frame_resize)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    camera.camera_close()
    cv2.destroyAllWindows()
    
    