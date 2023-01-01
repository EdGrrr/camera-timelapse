#! /bin/bash

# Cold-restart of GPS module - see https://ozzmaker.com/berrygps_imu-faq/

service gpsd stop
echo -e -n "\xb5\x62\x06\x04\x04\x00\xff\xff\x01\x00\x0e\x61" > /dev/serial0
service gpsd start
