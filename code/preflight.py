#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pre-flight check — ตรวจระบบโดรนก่อนใช้/ก่อนเรียน
ตรวจ: WiFi → เชื่อมต่อ → IMU (acc≈1g, gyro≈0) → attitude (ไม่ NaN)
รัน:  python preflight.py
"""
import os
import sys
import time
import math
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, 'cflib-esplane'))

# NOTE: keep output cp874-compatible (Thai console). Avoid symbols like ≈°✅.

URI = 'udp://192.168.43.42:2390'
SSID = 'ESP-DRONE_XXXX'  # XXXX = ตาม MAC ของบอร์ด (DIY หรือ official ก็ใช้แบบนี้)
PW = '12345678'

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig

GREEN = '\033[92m'; RED = '\033[91m'; YELLOW = '\033[93m'; CYAN = '\033[96m'
BOLD = '\033[1m'; RESET = '\033[0m'

results = []


def report(name, ok, detail='', hint=''):
    status = (GREEN + 'PASS') if ok else (RED + 'FAIL')
    results.append(ok)
    print('  [%s%s]  %s%s%s  %s' % (status, RESET, BOLD, name, RESET, detail))
    if not ok and hint:
        print('         %sTip: %s%s' % (YELLOW, hint, RESET))


print(BOLD + CYAN + '\n=== 1) เช็คการเชื่อมต่อ WiFi โดรน ===' + RESET)
print('   ต่อ WiFi: %s  (รหัส %s)' % (SSID, PW))
ping = subprocess.run(['ping', '-n', '1', '-w', '1500', '192.168.43.42'],
                      capture_output=True, text=True)
ok_ping = 'TTL=' in ping.stdout
report('ping ถึงโดรน 192.168.43.42', ok_ping,
       '',
       'เปิด WiFi โดรนแล้วหรือยัง (SSID ข้างบน)? ถ้า Windows เด้งกลับ WiFi บ้าน ให้ลบโปรไฟล์ WiFi บ้าน')

if not ok_ping:
    print(RED + '\nข้ามขั้นต่อไป — เชื่อมต่อ WiFi โดรนก่อนครับ' + RESET)
    sys.exit(1)

print(BOLD + CYAN + '\n=== 2) เชื่อมต่อ + อ่านเซนเซอร์ ===' + RESET)
cflib.crtp.init_drivers()
cf = Crazyflie()
raw = []
state = {'connected': False, 'err': ''}


def log_cb(ts, data, logconf):
    raw.append((logconf.name, dict(data)))


def connected(uri):
    state['connected'] = True
    lg = LogConfig(name='sens', period_in_ms=200)
    for v in ['acc.x', 'acc.y', 'acc.z', 'gyro.x']:
        lg.add_variable(v, 'float')
    cf.log.add_config(lg)
    lg.data_received_cb.add_callback(log_cb)
    lg.start()
    lg2 = LogConfig(name='att', period_in_ms=200)
    for v in ['stabilizer.roll', 'stabilizer.pitch', 'stabilizer.yaw']:
        lg2.add_variable(v, 'float')
    cf.log.add_config(lg2)
    lg2.data_received_cb.add_callback(log_cb)
    lg2.start()


cf.connected.add_callback(connected)
cf.connection_failed.add_callback(lambda u, m: state.update(err=str(m)))
cf.open_link(URI)

t0 = time.time()
while time.time() - t0 < 8 and len(raw) < 10:
    time.sleep(0.1)
cf.close_link()

# merge sens+att pairs into combined samples
sens = [d for n, d in raw if n == 'sens']
att = [d for n, d in raw if n == 'att']
samples = []
for s, a in zip(sens, att):
    m = dict(s)
    m.update(a)
    samples.append(m)

report('เชื่อมต่อกับโดรน', state['connected'], state['err'],
       'เช็คว่าโดรน boot ถึง "Ready to fly" หรือยัง (ดู log)')

if not state['connected'] or len(samples) < 3:
    print(RED + '\nข้อมูลไม่พอ — ตรวจ: โดรนติดไฟไหม / boot ถึง Ready to fly / WiFi หลุด?' + RESET)
    sys.exit(1)

print(BOLD + CYAN + '\n=== 3) ตรวจค่าที่อ่านได้ ===' + RESET)
acc_mags = []
gyros = []
nan_count = 0
for s in samples[-5:]:
    ax, ay, az = s['acc.x'], s['acc.y'], s['acc.z']
    acc_mags.append(math.sqrt(ax * ax + ay * ay + az * az))
    gyros.append(abs(s['gyro.x']))
    for k, v in s.items():
        if isinstance(v, float) and math.isnan(v):
            nan_count += 1

mag = sum(acc_mags) / len(acc_mags)
g = sum(gyros) / len(gyros)
report('accel รวม ~ %.2f g (ควรใกล้ 1.0)' % mag, 0.8 < mag < 1.2, '',
       'ถ้าออก 0 แปลว่า IMU หายจากบัส ให้ถอด-เสียบ USB ใหม่ (ปัญหา hardware สาย IMU)')
report('gyro ~ %.1f deg/s (ควรใกล้ 0)' % g, g < 5, '',
       'วางโดรนนิ่ง ๆ ตอน calibrate (~2 วิแรกหลังเปิด)')
report('attitude ไม่เป็น NaN', nan_count == 0, '(ค่า NaN: %d)' % nan_count,
       'ดู log boot: ต้องเห็น "Ready to fly."')

print(BOLD + CYAN + '\n=== สรุป ===' + RESET)
if all(results):
    print(GREEN + BOLD + '  [OK] พร้อมใช้งาน! เปิดสื่อการสอนแล้วเริ่มได้เลย' + RESET)
else:
    print(RED + BOLD + '  [X] ยังมีปัญหา - ดูคำแนะนำข้างบน' + RESET)
print()
