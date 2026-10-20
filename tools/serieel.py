"""Praat met de ESP32 via de seriële poort.

Voorbeelden:
  python tools/serieel.py --reset --sec 12        # herstart en lees 12 s
  python tools/serieel.py "t leds" --sec 6       # stuur commando, lees 6 s, stuur daarna Enter (stop)
"""
import argparse
import sys
import time

import serial

ap = argparse.ArgumentParser()
ap.add_argument("cmd", nargs="?", help="commando om te sturen")
ap.add_argument("--port", default="COM5")
ap.add_argument("--sec", type=float, default=5)
ap.add_argument("--reset", action="store_true", help="bord eerst herstarten")
ap.add_argument("--no-stop", action="store_true", help="na afloop geen Enter sturen")
a = ap.parse_args()

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
s = serial.Serial()
s.port, s.baudrate, s.timeout = a.port, 115200, 0.1
s.dtr = False  # openen zonder het bord te herstarten
s.rts = False
s.open()
if a.reset:
    s.rts = True
    time.sleep(0.1)
    s.rts = False
else:
    s.reset_input_buffer()
if a.cmd:
    time.sleep(0.2)
    s.write((a.cmd + "\n").encode())

end = time.time() + a.sec
while time.time() < end:
    data = s.read(4096)
    if data:
        sys.stdout.write(data.decode("utf-8", errors="replace"))
        sys.stdout.flush()
if a.cmd and not a.no_stop:
    s.write(b"\n")
    time.sleep(0.3)
    sys.stdout.write(s.read(4096).decode("utf-8", errors="replace"))
s.close()
