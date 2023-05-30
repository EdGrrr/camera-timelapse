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

interval = 5

# Assume that the wakeup is every hour at this time, so only set the
# minutes option. We are unlikely to want to sleep for longer than
# that.
pj.rtcAlarm.ClearAlarmFlag()
pj.rtcAlarm.SetAlarm({'minute': (t.minute+interval)%60})
pj.rtcAlarm.SetWakeupEnabled(True)

# Remove power to PiJuice MCU IO pins
pijuice.power.SetSystemPowerSwitch(0)

# Remove 5V power to RPi after 20 seconds
pijuice.power.SetPowerOff(20)

# Shut down the RPi
os.system("sudo halt")
