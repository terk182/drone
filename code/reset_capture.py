#!/usr/bin/env python3
"""Reset ESP32-S3 (native USB-Serial-JTAG) via RTS, then wait for the port to
re-enumerate, reopen, and capture the boot log.
Fixes: ClearCommError after reset (native USB handle dies on reset)."""
import serial, serial.tools.list_ports, time, sys

DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else 15
BAUD = 115200

def auto_port():
    env = __import__('os').environ.get('DRONE_PORT')
    if env:
        return env
    for p in serial.tools.list_ports.comports():
        desc = (p.description or '') + ' ' + (p.device or '')
        if any(k in desc.lower() for k in ('cp210', 'usb-serial', 'usb serial', 'usb jtag', 'esp32')):
            return p.device
    return 'COM10'

port = auto_port()
print(f'[1] reset {port} via RTS ...', flush=True)
s = serial.Serial(port, BAUD, timeout=0.1)
s.setDTR(False)
s.setRTS(True)
time.sleep(0.15)
s.setRTS(False)
s.close()  # native USB re-enumerates on reset -> handle dies, close immediately

print('[2] wait for port to re-appear ...', flush=True)
s2 = None
t0 = time.time()
while time.time() - t0 < 12:
    try:
        s2 = serial.Serial(port, BAUD, timeout=0.3)
        break
    except Exception:
        time.sleep(0.05)
if s2 is None:
    print('[fail] port did not come back', flush=True)
    sys.exit(1)

print(f'[3] capture {DURATION}s ...', flush=True)
buf = b''
t0 = time.time()
while time.time() - t0 < DURATION:
    try:
        d = s2.read(4096)
        if d:
            buf += d
    except Exception as e:
        print(f'[warn] read err {e} — reopen', flush=True)
        try:
            s2.close()
        except Exception:
            pass
        time.sleep(0.3)
        try:
            s2 = serial.Serial(port, BAUD, timeout=0.3)
        except Exception:
            pass
try:
    s2.close()
except Exception:
    pass

print(f'[done] bytes={len(buf)}', flush=True)
text = buf.decode('utf-8', errors='replace')
print(text[-7000:] if len(text) > 7000 else text)
