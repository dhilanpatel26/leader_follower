#!/usr/bin/env python3
import os
import sys
import time
sys.path.append('/home/pi/TurboPi/')
import RPi.GPIO as GPIO
from smbus2 import SMBus, i2c_msg
from rpi_ws281x import PixelStrip
from rpi_ws281x import Color as PixelColor

#幻尔科技raspberrypi扩展板sdk# Hiwonder Raspberry Pi expansion board sdk

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

__ADC_BAT_ADDR = 0
__SERVO_ADDR   = 21
__MOTOR_ADDR   = 31
__SERVO_ADDR_CMD  = 40

__motor_speed = [0, 0, 0, 0]
__servo_angle = [0, 0, 0, 0, 0, 0]
__servo_pulse = [0, 0, 0, 0, 0, 0]
__i2c = 1
__i2c_addr = 0x7A

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

__RGB_COUNT = 2
__RGB_PIN = 12
__RGB_FREQ_HZ = 800000
__RGB_DMA = 10
__RGB_BRIGHTNESS = 120
__RGB_CHANNEL = 0
__RGB_INVERT = False
RGB = PixelStrip(__RGB_COUNT, __RGB_PIN, __RGB_FREQ_HZ, __RGB_DMA, __RGB_INVERT, __RGB_BRIGHTNESS, __RGB_CHANNEL)
RGB.begin()
for i in range(RGB.numPixels()):
    RGB.setPixelColor(i, PixelColor(0,0,0))
    RGB.show()

def setMotor(index, speed):
    if index < 1 or index > 4:
        raise AttributeError("Invalid motor num: %d"%index)
    if index == 2 or index == 4:
        speed = speed
    else:
        speed = -speed
    index = index - 1
    speed = 100 if speed > 100 else speed
    speed = -100 if speed < -100 else speed
    reg = __MOTOR_ADDR + index
    
    with SMBus(__i2c) as bus:
        try:
            msg = i2c_msg.write(__i2c_addr, [reg, speed.to_bytes(1, 'little', signed=True)[0]])
            bus.i2c_rdwr(msg)
            __motor_speed[index] = speed
            
        except:
            msg = i2c_msg.write(__i2c_addr, [reg, speed.to_bytes(1, 'little', signed=True)[0]])
            bus.i2c_rdwr(msg)
            __motor_speed[index] = speed
           
    return __motor_speed[index]

     
def getMotor(index):
    if index < 1 or index > 4:
        raise AttributeError("Invalid motor num: %d"%index)
    index = index - 1
    return __motor_speed[index]

def setPWMServoAngle(index, angle):
    if servo_id < 1 or servo_id > 6:
        raise AttributeError("Invalid Servo ID: %d"%servo_id)
    index = servo_id - 1
    angle = 180 if angle > 180 else angle
    angle = 0 if angle < 0 else angle
    reg = __SERVO_ADDR + index
    with SMBus(__i2c) as bus:
        try:
            msg = i2c_msg.write(__i2c_addr, [reg, angle])
            bus.i2c_rdwr(msg)
            __servo_angle[index] = angle
            __servo_pulse[index] = int(((200 * angle) / 9) + 500)

        except:
            msg = i2c_msg.write(__i2c_addr, [reg, angle])
            bus.i2c_rdwr(msg)
            __servo_angle[index] = angle
            __servo_pulse[index] = int(((200 * angle) / 9) + 500)

    return __servo_angle[index]

def setPWMServoPulse(servo_id, pulse = 1500, use_time = 1000):
    if servo_id< 1 or servo_id > 6:
        raise AttributeError("Invalid Servo ID: %d" %servo_id)
    index = servo_id - 1
    pulse = 500 if pulse < 500 else pulse
    pulse = 2500 if pulse > 2500 else pulse
    use_time = 0 if use_time < 0 else use_time
    use_time = 30000 if use_time > 30000 else use_time
    buf = [__SERVO_ADDR_CMD, 1] + list(use_time.to_bytes(2, 'little')) + [servo_id,] + list(pulse.to_bytes(2, 'little'))
    
    with SMBus(__i2c) as bus:
        try:
            msg = i2c_msg.write(__i2c_addr, buf)
            bus.i2c_rdwr(msg)
            __servo_pulse[index] = pulse
            __servo_angle[index] = int((pulse - 500) * 0.09)
        except BaseException as e:
            print(e)
            msg = i2c_msg.write(__i2c_addr, buf)
            bus.i2c_rdwr(msg)
            __servo_pulse[index] = pulse
            __servo_angle[index] = int((pulse - 500) * 0.09)

    return __servo_pulse[index]

def setPWMServosPulse(args):
    ''' time,number, id1, pos1, id2, pos2...'''
    arglen = len(args)
    servos = args[2:arglen:2]
    pulses = args[3:arglen:2]
    use_time = args[0]
    use_time = 0 if use_time < 0 else use_time
    use_time = 30000 if use_time > 30000 else use_time
    servo_number = args[1]
    buf = [__SERVO_ADDR_CMD, servo_number] + list(use_time.to_bytes(2, 'little'))
    dat = zip(servos, pulses)
    for (s, p) in dat:
        buf.append(s)
        p = 500 if p < 500 else p
        p = 2500 if p > 2500 else p
        buf += list(p.to_bytes(2, 'little'))  
        __servo_pulse[s-1] = p
        __servo_angle[s-1] = int((p - 500) * 0.09)
     
    with SMBus(__i2c) as bus:
        try:
            msg = i2c_msg.write(__i2c_addr, buf)
            bus.i2c_rdwr(msg)
        except:
            msg = i2c_msg.write(__i2c_addr, buf)
            bus.i2c_rdwr(msg)


def getPWMServoAngle(servo_id):
    if servo_id < 1 or servo_id > 6:
        raise AttributeError("Invalid Servo ID: %d"%servo_id)
    index = servo_id - 1
    return __servo_pulse[index]

def getPWMServoPulse(servo_id):
    if servo_id < 1 or servo_id > 6:
        raise AttributeError("Invalid Servo ID: %d"%servo_id)
    index = servo_id - 1
    return __servo_pulse[index]
    
def getBattery():
    ret = 0
    with SMBus(__i2c) as bus:
        try:
            msg = i2c_msg.write(__i2c_addr, [__ADC_BAT_ADDR,])
            bus.i2c_rdwr(msg)
            read = i2c_msg.read(__i2c_addr, 2)
            bus.i2c_rdwr(read)
            ret = int.from_bytes(bytes(list(read)), 'little')
            
        except:
            msg = i2c_msg.write(__i2c_addr, [__ADC_BAT_ADDR,])
            bus.i2c_rdwr(msg)
            read = i2c_msg.read(__i2c_addr, 2)
            bus.i2c_rdwr(read)
            ret = int.from_bytes(bytes(list(read)), 'little')
           
    return ret

def setBuzzer(new_state):
    GPIO.setup(31, GPIO.OUT)
    GPIO.output(31, new_state)

def setBusServoID(oldid, newid):
    """
    配置舵机id号, 出厂默认为1  Configure servo ID number which is 1 by default
    :param oldid: 原来的id， 出厂默认为1  Old ID, which is 1 by default
    :param newid: 新的id  New ID
    """
    serial_serro_wirte_cmd(oldid, LOBOT_SERVO_ID_WRITE, newid)

def getBusServoID(id=None):
    """
    读取串口舵机id/ Read servo ID 
    :param id: 默认为空/ null by deafult 
    :return: 返回舵机id/ return servo ID
    """
    
    while True:
        if id is None:  # 总线上只能有一个舵机  only one servo on the bus
            serial_servo_read_cmd(0xfe, LOBOT_SERVO_ID_READ)
        else:
            serial_servo_read_cmd(id, LOBOT_SERVO_ID_READ)
        # 获取内容  Obtain content
        msg = serial_servo_get_rmsg(LOBOT_SERVO_ID_READ)
        if msg is not None:
            return msg

def setBusServoPulse(id, pulse, use_time):
    """
    驱动串口舵机转到指定位置   Drive servo to the specific position
    :param id: 要驱动的舵机id  servo ID to be driven
    :pulse: 位置 position
    :use_time: 转动需要的时间  running time
    """

    pulse = 0 if pulse < 0 else pulse
    pulse = 1000 if pulse > 1000 else pulse
    use_time = 0 if use_time < 0 else use_time
    use_time = 30000 if use_time > 30000 else use_time
    serial_serro_wirte_cmd(id, LOBOT_SERVO_MOVE_TIME_WRITE, pulse, use_time)

def stopBusServo(id=None):
    '''
    停止舵机运行 servo stops running 
    :param id:
    :return:
    '''
    serial_serro_wirte_cmd(id, LOBOT_SERVO_MOVE_STOP)

def setBusServoDeviation(id, d=0):
    """
    调整偏差  Ajust deviation
    :param id: 舵机id  servo ID
    :param d:  偏差    deviation
    """
    serial_serro_wirte_cmd(id, LOBOT_SERVO_ANGLE_OFFSET_ADJUST, d)

def saveBusServoDeviation(id):
    """
    配置偏差，掉电保护   configure deviation. Power off protection
    :param id: 舵机id    servo ID
    """
    serial_serro_wirte_cmd(id, LOBOT_SERVO_ANGLE_OFFSET_WRITE)

time_out = 50
def getBusServoDeviation(id):
    '''
    读取偏差值  read deviation
    :param id: 舵机号 servo ID
    :return:
    '''
    # 发送读取偏差指令  Send the command for reading deviation
    count = 0
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_ANGLE_OFFSET_READ)
        # 获取 Obtain
        msg = serial_servo_get_rmsg(LOBOT_SERVO_ANGLE_OFFSET_READ)
        count += 1
        if msg is not None:
            return msg
        if count > time_out:
            return None

def setBusServoAngleLimit(id, low, high):
    '''
    设置舵机转动范围 set servo turning range
    :param id:
    :param low:
    :param high:
    :return:
    '''
    serial_serro_wirte_cmd(id, LOBOT_SERVO_ANGLE_LIMIT_WRITE, low, high)

def getBusServoAngleLimit(id):
    '''
    读取舵机转动范围 read range 
    :param id: 
    :return: 返回元祖/return tuple 0： low-bit  1： high-bit
    '''
    
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_ANGLE_LIMIT_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_ANGLE_LIMIT_READ)
        if msg is not None:
            count = 0
            return msg

def setBusServoVinLimit(id, low, high):
    '''
    设置舵机电压范围  set servo voltage range
    :param id:
    :param low:
    :param high:
    :return:
    '''
    serial_serro_wirte_cmd(id, LOBOT_SERVO_VIN_LIMIT_WRITE, low, high)

def getBusServoVinLimit(id):
    '''
    读取舵机转动范围 read range 
    :param id:
    :return: 返回元祖 0： 低位  1： 高位 /return: return tuple 0： low-bit  1： high-bit
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_VIN_LIMIT_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_VIN_LIMIT_READ)
        if msg is not None:
            return msg

def setBusServoMaxTemp(id, m_temp):
    '''
    设置舵机最高温度报警  Set the servo maximum temperature alarm
    :param id:
    :param m_temp:
    :return:
    '''
    serial_serro_wirte_cmd(id, LOBOT_SERVO_TEMP_MAX_LIMIT_WRITE, m_temp)

def getBusServoTempLimit(id):
    '''
    读取舵机温度报警范围 read temperature alarming range
    :param id:
    :return:
    '''
    
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_TEMP_MAX_LIMIT_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_TEMP_MAX_LIMIT_READ)
        if msg is not None:
            return msg

def getBusServoPulse(id):
    '''
    读取舵机当前位置 read servo current position
    :param id:
    :return:
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_POS_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_POS_READ)
        if msg is not None:
            return msg

def getBusServoTemp(id):
    '''
    读取舵机温度 read servo temperature
    :param id:
    :return:
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_TEMP_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_TEMP_READ)
        if msg is not None:
            return msg

def getBusServoVin(id):
    '''
    读取舵机电压   read servo voltage
    :param id:
    :return:
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_VIN_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_VIN_READ)
        if msg is not None:
            return msg

def restBusServoPulse(oldid):
    # 舵机清零偏差和P值中位（500）   servo clear deviation and P value is set as 500
    serial_servo_set_deviation(oldid, 0)    # 清零偏差 clear deviation
    time.sleep(0.1)
    serial_serro_wirte_cmd(oldid, LOBOT_SERVO_MOVE_TIME_WRITE, 500, 100)    # 中位 middle position 

##掉电 Power off
def unloadBusServo(id):
    serial_serro_wirte_cmd(id, LOBOT_SERVO_LOAD_OR_UNLOAD_WRITE, 0)

##读取是否掉电 read whether it is power off
def getBusServoLoadStatus(id):
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_LOAD_OR_UNLOAD_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_LOAD_OR_UNLOAD_READ)
        if msg is not None:
            return msg

setBuzzer(0)

# setMotor(1, 60)
# setMotor(2, 60)
# setMotor(3, 60)
# setMotor(4, 60)

