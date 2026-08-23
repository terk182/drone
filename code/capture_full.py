"""Capture ALL drone serial output to a file (no filtering)."""
import os
import serial
import serial.tools.list_ports
import time

BAUD = 115200
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'boot_full.log')

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

s = serial.Serial(PORT, BAUD, timeout=0.2)

# Reset the chip via RTS (typical ESP32 dev reset wiring)
try:
    s.setDTR(False)
    s.setRTS(True)
    time.sleep(0.15)
    s.setRTS(False)
except Exception as e:
    print(f'reset warning: {e}')

end = time.time() + 45
with open(OUT, 'w', encoding='utf-8', errors='replace') as f:
    while time.time() < end:
        try:
            line = s.readline()
        except Exception as e:
            print(f'read error: {e}')
            break
        if not line:
            continue
        f.write(line.decode(errors='replace'))

s.close()
print('--- saved to', OUT, '---')
