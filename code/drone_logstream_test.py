#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demonstrate Python seeing live drone data via cflib log.
Streams IMU + motor PWM from the drone and prints every sample.
"""
import os
import sys
import time
import threading

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cflib-esplane'))

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig

URI = 'udp://192.168.43.42:2390'
cflib.crtp.init_drivers()

cf = Crazyflie()
log_conf = None
count = 0


def log_cb(timestamp, data, logconf):
    global count
    count += 1
    print('DATA[%d]: t=%d acc.z=%.3f gyro.x=%.2f | PWM m1=%d m2=%d m3=%d m4=%d' % (
        count, timestamp, data['acc.z'], data['gyro.x'],
        data['pwm.m1_pwm'], data['pwm.m2_pwm'], data['pwm.m3_pwm'], data['pwm.m4_pwm']))


def connected(link_uri):
    print('>>> CONNECTED')
    global log_conf
    log_conf = LogConfig(name='imu', period_in_ms=100)
    log_conf.add_variable('acc.z', 'float')
    log_conf.add_variable('gyro.x', 'float')
    log_conf.add_variable('pwm.m1_pwm', 'uint32_t')
    log_conf.add_variable('pwm.m2_pwm', 'uint32_t')
    log_conf.add_variable('pwm.m3_pwm', 'uint32_t')
    log_conf.add_variable('pwm.m4_pwm', 'uint32_t')
    cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(log_cb)
    log_conf.start()
    print('>>> LOG streaming started')


def conn_failed(uri, msg):
    print('>>> CONNECT FAILED:', msg)


def disconn(uri):
    print('>>> DISCONNECTED')


def sender():
    # continuous: unlock 1s -> thrust 25000 4s -> stop 1s
    seq = [(0, 1), (25000, 4), (0, 1)]
    for thrust, dur in seq:
        t0 = time.time()
        while time.time() - t0 < dur:
            cf.commander.send_setpoint(0, 0, 0, thrust)
            time.sleep(0.05)


cf.connected.add_callback(connected)
cf.connection_failed.add_callback(conn_failed)
cf.disconnected.add_callback(disconn)

print('>>> Opening', URI)
cf.open_link(URI)
time.sleep(8)

print('>>> Streaming data (10s idle)...')
time.sleep(3)

print('>>> Now sending thrust (motors spin) while streaming...')
th = threading.Thread(target=sender)
th.start()
# main thread stays free: sleep in small chunks so callbacks always fire
while th.is_alive():
    time.sleep(0.5)
time.sleep(2)

print('>>> Total data samples received: %d' % count)
cf.close_link()
print('>>> DONE')
