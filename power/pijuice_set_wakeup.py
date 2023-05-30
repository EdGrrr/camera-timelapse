#! /usr/bin/python3

# Script to ensure a suitable wakeup time is always 10 min in the future incase of unexpected power loss
# Also makes sure power on charge is on and the watchdog

import pijuice
import subprocess
import datetime
import os
import time

# This script is started at reboot by cron.
# Since the start is very early in the boot sequence we wait for the i2c-1 device
while not os.path.exists('/dev/i2c-1'):
    time.sleep(0.1)

# This would only be done at startup, so probably not here
# subprocess.call(["sudo", "hwclock", "--hctosys"])

pj = pijuice.PiJuice(1, 0x14)

# Copy the system clock to the RTC
t = datetime.datetime.utcnow()
pj.rtcAlarm.SetTime({
    'second': t.second,
    'minute': t.minute,
    'hour': t.hour,
    'weekday': t.weekday() + 1,
    'day': t.day,
    'month': t.month,
    'year': t.year,
    'subsecond': t.microsecond // 1000000
})

# Sleep at 3% charge
# This is set by the pijuice config file and service. Don't need to set here

#Wakeup at 5% charge
pj.power.SetWakeUpOnCharge(5, True)

# Set alarm details in the abscence of anything else
pj.rtcAlarm.ClearAlarmFlag()
pj.rtcAlarm.SetAlarm({'minute_period': 10})
pj.rtcAlarm.SetWakeupEnabled(True)
