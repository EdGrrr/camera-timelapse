#!/usr/bin/python3

import pijuice
import os
pijuice = pijuice.PiJuice(1, 0x14)

# Remove power to PiJuice MCU IO pins
pijuice.power.SetSystemPowerSwitch(0)

# Remove 5V power to RPi after 20 seconds
pijuice.power.SetPowerOff(20)

# Shut down the RPi
os.system("sudo halt")
