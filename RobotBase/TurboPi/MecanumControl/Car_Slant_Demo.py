#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/TurboPi/')
import time
import signal
import HiwonderSDK.mecanum as mecanum

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
    
print('''
**********************************************************
*******************功能:小车斜向移动例程 Function: Oblique motion*********************
**********************************************************
----------------------------------------------------------
Official website:https://www.hiwonder.com
Online mall:https://hiwonder.tmall.com
----------------------------------------------------------
Tips:
 * 按下Ctrl+C可关闭此次程序运行，若失败请多次尝试！ Press Ctrl+C to exit the program, please try few more times if fail to exit!
----------------------------------------------------------
''')

chassis = mecanum.MecanumChassis()

start = True
#关闭前处理 Processing before exit 
def Stop(signum, frame):
    global start

    start = False
    print('closing...')
    chassis.set_velocity(0,0,0)  # 关闭所有电机 Turn off all motors 
    

signal.signal(signal.SIGINT, Stop)

if __name__ == '__main__':
    while start:
        chassis.set_velocity(50,45,0) # 控制机器人移动函数,线速度50(0~100)，方向角45(0~360)，偏航角速度0(-2~2) Movement control function. The linear velocity is 50 (0~100). The direcion angle is 180 (0-350). The jaw velocity is 0.3 (-2~2).
        time.sleep(1)
        chassis.set_velocity(50,315,0)
        time.sleep(1)
        chassis.set_velocity(50,225,0)
        time.sleep(1)
        chassis.set_velocity(50,135,0)
        time.sleep(1)
    chassis.set_velocity(0,0,0)  # 关闭所有电机 Turn off all motors 
    print('Closed')

        
