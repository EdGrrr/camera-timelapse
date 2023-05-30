#!/usr/bin/python3

import pijuice
import os
import datetime

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

# Wakeup at 57 min to hour
pj.rtcAlarm.ClearAlarmFlag()
pj.rtcAlarm.SetAlarm({'minute': 57})
pj.rtcAlarm.SetWakeupEnabled(True)

# Remove power to PiJuice MCU IO pins
pj.power.SetSystemPowerSwitch(0)

# Remove 5V power to RPi after 20 seconds
pj.power.SetPowerOff(20)

# Shut down the RPi
os.system("sudo halt")
