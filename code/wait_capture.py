#!/usr/bin/env python3
"""Wait for a new COM port, then capture boot output immediately (no reset)."""
import sys, time, serial, serial.tools.list_ports

DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else 25
seen = set(p.device for p in serial.tools.list_ports.comports())
print("[wait] watching for new COM port...", flush=True)

port = None
while port is None:
    for p in serial.tools.list_ports.comports():
        if p.device not in seen:
            port = p.device
            break
    time.sleep(0.2)

print(f"[wait] port appeared: {port} — capturing {DURATION}s (no reset)", flush=True)

buf = b''
t0 = time.time()
while time.time() - t0 < DURATION:
    try:
        s = serial.Serial(port, 115200, timeout=0.3)
        break
    except Exception:
        time.sleep(0.2)
else:
    print("[fail] could not open port", flush=True)
    sys.exit(1)

print(f"[wait] listening on {port} ...", flush=True)
while time.time() - t0 < DURATION:
    try:
        d = s.read(4096)
        if d:
            buf += d
    except Exception as e:
        # port hiccup (this board's USB is flaky) — reopen and continue
        print(f"[warn] read error {e} — reopening", flush=True)
        try:
            s.close()
        except Exception:
            pass
        try:
            s = serial.Serial(port, 115200, timeout=0.3)
        except Exception:
            time.sleep(0.3)
try:
    s.close()
except Exception:
    pass

print(f"[done] total bytes: {len(buf)}", flush=True)
text = buf.decode('utf-8', errors='replace')
print(text[-6000:] if len(text) > 6000 else text)
