"""Reset the board repeatedly and check whether imu_test reliably reads the MPU."""
import os
import serial
import serial.tools.list_ports
import time

BAUD = 115200

def find_port():
    env = os.environ.get('DRONE_PORT')
    if env:
        return env
    for p in serial.tools.list_ports.comports():
        desc = (p.description or '') + ' ' + (p.device or '')
        if any(k in desc.lower() for k in ('cp210', 'usb-serial', 'usb serial', 'usb jtag', 'esp32')):
            return p.device
    return 'COM3'

PORT = find_port()

def reset(s):
    s.setDTR(False)
    s.setRTS(True)
    time.sleep(0.15)
    s.setRTS(False)

s = serial.Serial(PORT, BAUD, timeout=0.3)

for run in range(10):
    reset(s)
    ok_scan = ok_who = False
    end = time.time() + 6
    buf = []
    while time.time() < end:
        line = s.readline()
        if not line:
            continue
        txt = line.decode(errors='replace').strip()
        if 'device found at 0x68' in txt:
            ok_scan = True
        if 'WHO_AM_I = 0x70' in txt:
            ok_who = True
            buf.append(txt)
        if 'sample 0:' in txt:
            buf.append(txt)
    status = 'OK ' if (ok_scan and ok_who) else 'FAIL'
    print(f'run {run}: {status} scan={ok_scan} who={ok_who} {" | ".join(buf[-2:])}')

s.close()
