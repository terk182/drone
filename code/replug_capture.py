#!/usr/bin/env python3
"""Wait for the user to unplug + replug the drone USB, then capture boot log
immediately (no reset). Fixes: stale COM port (PermissionError 13) and
re-latched clone IMU after software reset."""
import sys, time, serial, serial.tools.list_ports

DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else 20

# remember current ports so we can detect disappear + reappear
def now_ports():
    return set(p.device for p in serial.tools.list_ports.comports())

before = now_ports()
print(f"[1] พอร์ตปัจจุบัน: {sorted(before)}", flush=True)
print("[1] กรุณา ถอดสาย USB ออกจากบอร์ด ... (รอสูงสุด 60 วิ)", flush=True)

# step 1: wait for any current port to DISAPPEAR (unplug)
gone = None
t0 = time.time()
while time.time() - t0 < 60:
    cur = now_ports()
    missing = before - cur
    if missing:
        gone = missing.pop()
        print(f"[2] เห็นพอร์ตหายไป: {gone} -> เสียบกลับใหม่ได้เลย!", flush=True)
        break
    time.sleep(0.2)
else:
    print("[fail] ไม่เห็นการถอดสาย (60 วิ) — ลองถอดแล้วเสียบใหม่ แล้วรันใหม่", flush=True)
    sys.exit(1)

# step 2: wait for a port to reappear (replug) — could be same or new name
port = None
t0 = time.time()
while time.time() - t0 < 60:
    cur = now_ports()
    new = cur - before
    if gone in cur or new:
        port = gone if gone in cur else new.pop()
        break
    time.sleep(0.2)
if port is None:
    print("[fail] ไม่เห็นพอร์ตกลับมา (60 วิ)", flush=True)
    sys.exit(1)
print(f"[3] พอร์ตกลับมา: {port} — เริ่มจับ boot {DURATION} วิ (ไม่ reset)", flush=True)

buf = b''
t0 = time.time()
s = None
while time.time() - t0 < DURATION:
    try:
        if s is None:
            s = serial.Serial(port, 115200, timeout=0.3)
        d = s.read(4096)
        if d:
            buf += d
    except Exception as e:
        print(f"[warn] read error {e} — reopening", flush=True)
        try:
            if s: s.close()
        except Exception:
            pass
        s = None
        time.sleep(0.2)
try:
    if s: s.close()
except Exception:
    pass

print(f"[done] total bytes: {len(buf)}", flush=True)
text = buf.decode('utf-8', errors='replace')
print(text[-8000:] if len(text) > 8000 else text)
