#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ESP-Drone motor test (cflib esplane fork, UDP driver)
- Connect via UDP
- Log ONLY motor PWM (minimal traffic)
- Send thrust continuously (like the phone app) and watch PWM rise
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
pwm_log = []


def log_cb(timestamp, data, logconf):
    pwm_log.append(data['pwm.m1_pwm'])
    print('PWM: m1=%5d m2=%5d m3=%5d m4=%5d' % (
        data['pwm.m1_pwm'], data['pwm.m2_pwm'], data['pwm.m3_pwm'], data['pwm.m4_pwm']))


def connected(link_uri):
    print('>>> CONNECTED to %s' % link_uri)
    global log_conf
    log_conf = LogConfig(name='pwm', period_in_ms=200)
    log_conf.add_variable('pwm.m1_pwm', 'uint32_t')
    log_conf.add_variable('pwm.m2_pwm', 'uint32_t')
    log_conf.add_variable('pwm.m3_pwm', 'uint32_t')
    log_conf.add_variable('pwm.m4_pwm', 'uint32_t')
    try:
        cf.log.add_config(log_conf)
        log_conf.data_received_cb.add_callback(log_cb)
        log_conf.start()
        print('>>> LOG started (motor PWM)')
    except Exception as e:
        print('>>> LOG start error:', e)


def conn_failed(link_uri, msg):
    print('>>> CONNECT FAILED:', msg)


def disconn(link_uri):
    print('>>> DISCONNECTED')


cf.connected.add_callback(connected)
cf.connection_failed.add_callback(conn_failed)
cf.disconnected.add_callback(disconn)

print('>>> Opening link:', URI)
cf.open_link(URI)
time.sleep(8)  # wait for connect + log start

# Phase 1: zero thrust to unlock thrustLocked
print('>>> PHASE 1: zero thrust (unlock) 2s...')
t0 = time.time()
while time.time() - t0 < 2:
    cf.commander.send_setpoint(0, 0, 0, 0)
    time.sleep(0.02)

# Phase 2: thrust 20000 for 5s (motors should spin!)
print('>>> PHASE 2: thrust=20000 for 5s - MOTORS SHOULD SPIN!')
t0 = time.time()
while time.time() - t0 < 5:
    cf.commander.send_setpoint(0, 0, 0, 20000)
    time.sleep(0.02)

# Phase 3: stop
print('>>> PHASE 3: stop')
t0 = time.time()
while time.time() - t0 < 1:
    cf.commander.send_setpoint(0, 0, 0, 0)
    time.sleep(0.02)

# Summary
if pwm_log:
    print('>>> Max PWM seen: %d' % max(pwm_log))
    print('>>> Motor PWM raised above zero: %s' % ('YES' if max(pwm_log) > 0 else 'NO'))

cf.close_link()
print('>>> DONE')
