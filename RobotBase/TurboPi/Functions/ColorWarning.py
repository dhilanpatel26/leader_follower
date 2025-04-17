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
import HiwonderSDK.Board as Board

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)


servo1 = 1500
servo2 = 1500
color_list = []
size = (640, 480)
interval_time = 0
__isRunning = False
detect_color = 'None'
target_color = ('red', 'green', 'blue')

lab_data = None
servo_data = None
def load_config():
    global lab_data, servo_data
    global servo1, servo2
    
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)
    servo1 = servo_data['servo1']
    servo2 = servo_data['servo2']

# 初始位置 initial position
def initMove():
    Board.setPWMServoPulse(1, servo1, 1000)
    Board.setPWMServoPulse(2, servo2, 1000)
    
# 初始化调用 Initialization
def init():
    print("ColorWarning Init")
    load_config()
    initMove()

# 开始玩法调用 start game
def start():
    global __isRunning
    __isRunning = True
    print("ColorWarning Start")

# 设置蜂鸣器 set buzzer
def setBuzzer(timer):
    Board.setBuzzer(0)
    Board.setBuzzer(1)
    time.sleep(timer)
    Board.setBuzzer(0)

range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

# 找出面积最大的轮廓 find the maximum contour
# 参数为要比较的轮廓的列表 the parameterts is the list of the contours to be coompared
def getAreaMaxContour(contours):
    contour_area_max = 0
    contour_area_temp = 0
    area_max_contour = None

    for c in contours:  # 历遍所有轮廓 Traverse all contours
        contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积 calculate the contour area
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 300:  # 只有在面积大于300时，最大面积的轮廓才是有效的，以过滤干扰 Only if the area is greater than 300, the maximum contour takes effect to file the inteference
                area_max_contour = c

    return area_max_contour, contour_area_max  # 返回最大的轮廓 Retune to the maximum contour
   

#设置扩展板的RGB灯颜色使其跟要追踪的颜色一致 Set the RGB light color of the expansion board to match the color to be tracked
def set_rgb(color):
    if color == "red":
        Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
        Board.RGB.show()
    elif color == "green":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
        Board.RGB.show()
    elif color == "blue":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
        Board.RGB.show()
    else:
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
        Board.RGB.show()


draw_color = range_rgb["black"]

def run(img):
    global interval_time
    global __isRunning, color_list
    global detect_color, draw_color
    
    if not __isRunning:  # 检测是否开启玩法，没有开启则返回原图像 Detect whether the game is turned on. If not, return the orginal piture.
        return img

    img_copy = img.copy()
    img_h, img_w = img.shape[:2]
    
    frame_resize = cv2.resize(img_copy, size, interpolation=cv2.INTER_NEAREST)
    frame_gb = cv2.GaussianBlur(frame_resize, (3, 3), 3)
    frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # 将图像转换到LAB空间 convert the image into LAB space
    
    max_area = 0
    color_area_max = None
    areaMaxContour_max = 0
    for i in target_color:
        if i in lab_data:
            frame_mask = cv2.inRange(frame_lab,
                                         (lab_data[i]['min'][0],
                                          lab_data[i]['min'][1],
                                          lab_data[i]['min'][2]),
                                         (lab_data[i]['max'][0],
                                          lab_data[i]['max'][1],
                                          lab_data[i]['max'][2]))  #对原图像和掩模进行位运算  Perform bit operation on the orignal picture and mask
            opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 Open 
            closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))  # 闭运算 Close
            contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # 找出轮廓 Find contour
            areaMaxContour, area_max = getAreaMaxContour(contours)  # 找出最大轮廓 The maximum contour is found
            if areaMaxContour is not None:
                if area_max > max_area:  # 找最大面积 find the maximux area
                    max_area = area_max
                    color_area_max = i
                    areaMaxContour_max = areaMaxContour
                    
    if max_area > 2500:  # 有找到最大面积 the maximum area is found 
        rect = cv2.minAreaRect(areaMaxContour_max)
        box = np.int0(cv2.boxPoints(rect))
        cv2.drawContours(img, [box], -1, range_rgb[color_area_max], 2)
        if color_area_max == 'red':  # 红色最大 red is the maximum contour
            color = 1
        elif color_area_max == 'green':  # 绿色最大 green is the maximum contour
            color = 2
        elif color_area_max == 'blue':  # 蓝色最大 blue is the maximum contour
            color = 3
        else:
            color = 0
        color_list.append(color)
        if len(color_list) == 3:  # 多次判断 Judge multiple times
            # averaging
            color = np.mean(np.array(color_list))
            color_list = []
            if color == 1:
                if time.time() > interval_time:
                    interval_time = time.time() + 3
                    for i in range(1):
                        setBuzzer(0.1)
                        time.sleep(0.1)
                detect_color = 'red'
                draw_color = range_rgb["red"]
            elif color == 2:
                detect_color = 'green'
                draw_color = range_rgb["green"]
            elif color == 3:  
                detect_color = 'blue'
                draw_color = range_rgb["blue"]
            else:
                detect_color = 'None'
                draw_color = range_rgb["black"]
    else:
        detect_color = 'None'
        draw_color = range_rgb["black"]
    
    cv2.putText(img, "Color: " + detect_color, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, draw_color, 2) # 把检测到的颜色打印在画面上  Print the detected color on image
    
    return img

#关闭前处理 Process before close
def manual_stop(signum, frame):
    global __isRunning
    
    print('closing...')
    __isRunning = False


if __name__ == '__main__':
    init()
    start()
    camera = Camera.Camera()
    camera.camera_open(correction=True) # 开启畸变矫正,默认不开启 start distortion correction which is closed by default.
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

