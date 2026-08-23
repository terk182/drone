#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ESP-Drone Python test (cflib with UDP driver)
- Connect to drone over WiFi UDP
- Read IMU log (gyro/acc) to prove data flow
- Send thrust to spin motors (verify calibration fix)
URI: udp://192.168.43.42:2390
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cflib-esplane'))

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig

URI = 'udp://192.168.43.42:2390'
cflib.crtp.init_drivers()

cf = Crazyflie()
log_conf = None


def log_cb(timestamp, data, logconf):
    print('LOG: t=%6d acc.z=%6.2f gyro.x=%6.2f | PWM m1=%5d m2=%5d m3=%5d m4=%5d' % (
        timestamp, data['acc.z'], data['gyro.x'],
        data['pwm.m1_pwm'], data['pwm.m2_pwm'], data['pwm.m3_pwm'], data['pwm.m4_pwm']))


def start_log():
    global log_conf
    log_conf = LogConfig(name='imu', period_in_ms=100)
    log_conf.add_variable('gyro.x', 'float')
    log_conf.add_variable('acc.z', 'float')
    log_conf.add_variable('pwm.m1_pwm', 'uint32_t')
    log_conf.add_variable('pwm.m2_pwm', 'uint32_t')
    log_conf.add_variable('pwm.m3_pwm', 'uint32_t')
    log_conf.add_variable('pwm.m4_pwm', 'uint32_t')
    try:
        cf.log.add_config(log_conf)
        log_conf.data_received_cb.add_callback(log_cb)
        log_conf.start()
        print('>>> LOG started (gyro/acc + motor PWM)')
    except Exception as e:
        print('>>> LOG start error:', e)


def connected(link_uri):
    print('>>> CONNECTED to %s' % link_uri)
    try:
        ctrl = cf.param.get_value('stabilizer.controller')
        print('>>> stabilizer.controller =', ctrl)
    except Exception as e:
        print('>>> param read error:', e)
    start_log()


def conn_failed(link_uri, msg):
    print('>>> CONNECT FAILED:', msg)


def disconn(link_uri):
    print('>>> DISCONNECTED')


cf.connected.add_callback(connected)
cf.connection_failed.add_callback(conn_failed)
cf.disconnected.add_callback(disconn)

print('>>> Opening link:', URI)
cf.open_link(URI)

# Wait for connection + TOC + log start
time.sleep(8)

# 1) Send zero thrust first (unlock thrustLocked safety in firmware)
print('>>> Send zero thrust (unlock)...')
cf.commander.send_setpoint(0, 0, 0, 0)
time.sleep(1)

# 2) Send thrust to spin motors
print('>>> Send thrust=12000 (motors should SPIN!) for 3s...')
cf.commander.send_setpoint(0, 0, 0, 12000)
time.sleep(3)
cf.commander.send_setpoint(0, 0, 0, 0)
print('>>> Thrust off')

time.sleep(1)
cf.close_link()
print('>>> DONE')
