#!/usr/bin/env python3
import datetime
import time

now = datetime.datetime.now()
week = now.isocalendar()[1]
tz = time.strftime("%Z")
formatted = now.strftime(f"%a %Y-%m-%d %H:%M:%S {tz}")
print(f"Timestamp: {formatted} (Week {week:02d})")
