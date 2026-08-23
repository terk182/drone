#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Diagnose NaN in log values: read accel, gyro, attitude, stateEstimate."""
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


def log_cb(timestamp, data, logconf):
    if logconf.name == 'sens':
        print('SENS: acc.x=%.3f acc.y=%.3f acc.z=%.3f gyro.x=%.2f' % (
            data['acc.x'], data['acc.y'], data['acc.z'], data['gyro.x']))
    else:
        print('ATT: stab.roll=%.2f stab.pitch=%.2f stab.yaw=%.2f est.z=%.2f vbat=%.2f' % (
            data['stabilizer.roll'], data['stabilizer.pitch'], data['stabilizer.yaw'],
            data['stateEstimate.z'], data['pm.vbat']))


def connected(uri):
    print('>>> CONNECTED')
    # Block A: sensors
    lgA = LogConfig(name='sens', period_in_ms=200)
    for v in ['acc.x', 'acc.y', 'acc.z', 'gyro.x']:
        lgA.add_variable(v, 'float')
    cf.log.add_config(lgA)
    lgA.data_received_cb.add_callback(log_cb)
    lgA.start()
    # Block B: attitude
    lgB = LogConfig(name='att', period_in_ms=200)
    for v in ['stabilizer.roll', 'stabilizer.pitch', 'stabilizer.yaw', 'stateEstimate.z', 'pm.vbat']:
        lgB.add_variable(v, 'float')
    cf.log.add_config(lgB)
    lgB.data_received_cb.add_callback(log_cb)
    lgB.start()
    print('>>> LOG started (2 blocks)')


def conn_failed(uri, msg):
    print('>>> CONNECT FAILED:', msg)


def disconn(uri):
    print('>>> DISCONNECTED')


cf.connected.add_callback(connected)
cf.connection_failed.add_callback(conn_failed)
cf.disconnected.add_callback(disconn)

print('>>> Opening', URI)
cf.open_link(URI)
time.sleep(12)
cf.close_link()
print('>>> DONE')
