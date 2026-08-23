#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ESP-Drone motor test v2 - threaded sender so log callbacks keep firing
during thrust (proves PWM reaches motors).
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
pwm_samples = []


def log_cb(timestamp, data, logconf):
    m1 = data['pwm.m1_pwm']
    pwm_samples.append(m1)
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


def thrust_loop(thrust, duration):
    t0 = time.time()
    while time.time() - t0 < duration:
        cf.commander.send_setpoint(0, 0, 0, thrust)
        time.sleep(0.02)


cf.connected.add_callback(connected)
cf.connection_failed.add_callback(conn_failed)
cf.disconnected.add_callback(disconn)

print('>>> Opening link:', URI)
cf.open_link(URI)
time.sleep(8)  # connect + log start

# Continuous stream (NO gaps > 500ms!):
#   1) thrust=0 for 1s  -> unlock thrustLocked + keep priority active
#   2) thrust=20000 for 5s -> motors spin
#   3) thrust=0 for 1s -> stop
def continuous_test():
    seq = [(0, 1.0), (20000, 5.0), (0, 1.0)]
    for thrust, dur in seq:
        t0 = time.time()
        while time.time() - t0 < dur:
            cf.commander.send_setpoint(0, 0, 0, thrust)
            time.sleep(0.02)

print('>>> Running continuous thrust test (unlock -> 20000 for 5s) - MOTORS SHOULD SPIN!')
pwm_samples.clear()
th = threading.Thread(target=continuous_test)
th.start()
# let the sender thread run; keep main thread pumping so log callbacks fire
th.join(timeout=9)
time.sleep(1)

if pwm_samples:
    print('>>> MAX PWM observed: %d (samples=%d)' % (max(pwm_samples), len(pwm_samples)))
    print('>>> MOTORS RECEIVE POWER: %s' % ('YES' if max(pwm_samples) > 0 else 'NO'))
else:
    print('>>> No PWM samples captured during thrust')

cf.close_link()
print('>>> DONE')
