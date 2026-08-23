"""Read drone boot/sensor output from the drone serial port, reset via RTS."""
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

KEYWORDS = ('accScale', 'WHO_AM_I', 'Ready to fly', 'isBiasValueFound',
            'rst:', 'I2C connection', 'I2CRAW', 'SENSORS', 'STAB',
            'MPU6050', 'VL53L1X', 'I2CDEV', 'SYSLOAD', 'pitch_calib')

s = serial.Serial(PORT, BAUD, timeout=0.2)

# Reset the chip: EN line via RTS (typical ESP32 dev reset wiring)
try:
    s.setDTR(False)
    s.setRTS(True)
    time.sleep(0.15)
    s.setRTS(False)
except Exception as e:
    print(f'reset warning: {e}')

end = time.time() + 40
count = 0
while time.time() < end:
    try:
        line = s.readline()
    except Exception as e:
        print(f'read error: {e}')
        break
    if not line:
        continue
    txt = line.decode(errors='replace').strip()
    if any(k in txt for k in KEYWORDS):
        print(txt)
        count += 1
        if count > 120:
            break

s.close()
print('--- capture done ---')
