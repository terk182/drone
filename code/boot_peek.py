"""Peek boot log WITHOUT resetting the board (just open port and read).
Use this to verify the IMU after a real power cycle (unplug/replug),
because a software reset re-latches the clone IMU."""
import os
import serial
import serial.tools.list_ports
import time
import sys

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
KEYWORDS = ('WHO_AM_I', 'I2C connection', 'sensors init', 'Ready to fly',
            'Wait for sensor', 'rst:', 'softap', 'Connection')

print('Open', PORT, '(no reset) ...')
s = serial.Serial(PORT, BAUD, timeout=0.3)
end = time.time() + 20
while time.time() < end:
    line = s.readline()
    if not line:
        continue
    txt = line.decode(errors='replace').strip()
    if any(k in txt for k in KEYWORDS):
        print(txt)
s.close()
print('--- done ---')
