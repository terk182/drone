#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test runner: runs cflib examples against the ESP-Drone over UDP.
Sets CFLIB_URI=udp://192.168.43.42:2390 and runs each example with a timeout.
"""
import os
import subprocess
import sys
import time

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cflib-esplane', 'examples')
URI = 'udp://192.168.43.42:2390'

# Examples testable on this drone (no extra decks needed)
TESTABLES = [
    ('logging/basiclog.py', 25),
    ('logging/basiclogSync.py', 25),
    ('parameters/basicparam.py', 25),
    ('step-by-step/sbs_connect_log_param.py', 25),
    ('basicLedTiming.py', 15),
    ('basicLedparamSync.py', 20),
    ('basicLedmemSync.py', 20),
    ('motors/ramp.py', 20),        # SPINS MOTORS
    ('motors/multiramp.py', 20),   # SPINS MOTORS
    ('console/console.py', 20),
]


def run_one(name, timeout):
    path = os.path.join(EXAMPLES_DIR, name)
    env = dict(os.environ)
    env['CFLIB_URI'] = URI
    print('=' * 70)
    print('>>> RUNNING: %s (timeout %ss)' % (name, timeout))
    print('=' * 70)
    t0 = time.time()
    try:
        p = subprocess.run(
            [sys.executable, path],
            capture_output=True, text=True, timeout=timeout, env=env,
            cwd=EXAMPLES_DIR)
        out = (p.stdout or '') + (p.stderr or '')
        ret = p.returncode
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or '') + (e.stderr or '')
        if isinstance(e.stdout, bytes):
            out = e.stdout.decode(errors='replace')
        ret = 'TIMEOUT'
    elapsed = time.time() - t0

    # Judgement
    connected = 'onnected' in out
    got_data = ('data' in out.lower()) or ('LOG' in out) or ('PWM' in out) or ('Error' not in out)
    # simple pass criteria: connected and (some output or no hard failure)
    fail_markers = ['Traceback', 'failed:', 'Could not', 'Error ']
    hard_fail = any(m in out for m in fail_markers)
    status = 'PASS' if (connected and not hard_fail) else ('PARTIAL' if connected else 'FAIL')
    print('--- OUTPUT (last 2000 chars) ---')
    print(out[-2000:])
    print('--- RESULT: %s (ret=%s, %.1fs) ---' % (status, ret, elapsed))
    return name, status, out


def main():
    results = []
    for name, timeout in TESTABLES:
        name, status, out = run_one(name, timeout)
        results.append((name, status))
        print()
    print('=' * 70)
    print('SUMMARY')
    print('=' * 70)
    for name, status in results:
        print('%-45s %s' % (name, status))


if __name__ == '__main__':
    main()
