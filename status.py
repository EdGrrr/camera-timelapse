#! /bin/python3

import os
import re
import subprocess
import json
import datetime
import sys

def get_process_output(proc):
    process = subprocess.Popen(proc, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    return output

try:
    outputfile = sys.argv[1]
except:
    outputfile = 'status.json'


status = {}

# Freespace
df_output = get_process_output(['df', '-h'])
df_usb = [b for b in
          [ a for a in df_output.decode('ascii').split('\n')
            if 'USB' in a][0].split(' ')
          if b != '']
status['freespace'] = df_usb[3]
status['usb_usage'] = df_usb[4]

# Timelapse status
timelapse_running = [b for b in
                     get_process_output(['systemctl', 'show', 'camera-timelapse']).decode('ascii').split('\n')
                     if b.startswith('ActiveState=')][0].split('=')[1]
status['timelapse_status'] = timelapse_running
timelapse_timer = [b for b in
                   get_process_output(['systemctl', 'show', 'camera-timelapse.timer']).decode('ascii').split('\n')
                   if b.startswith('ActiveState=')][0].split('=')[1]
status['timelapse_timer'] = timelapse_timer


# GPS status
gps_output = get_process_output(['gpspipe', '-w', '-n 10']).decode('ascii')
x  = re.search("mode\":(.),.*lat\":(\d*.\d*),.*lon\":(.*?\..*?),", gps_output)
try:
    status['gps_status'] = x.groups()[0]
except:
    status['gps_status'] = None
try:
    status['gps_lon'] = x.groups()[2]
    status['gps_lat'] = x.groups()[1]
except:
    status['gps_lon'] = None
    status['gps_lat'] = None

# NTP status
ntpd_output = get_process_output(['ntpq', '-p']).decode('ascii').split('\n')
status['ntp_pps_status'] = [b for b in ntpd_output if 'PPS' in b][0][0]
status['ntp_pps_checktime'] = list(filter(None, [b for b in ntpd_output if 'PPS' in b][0].split(' ')))[4]
status['ntp_gps_status'] = [b for b in ntpd_output if 'GPS' in b][0][0]
status['ntp_janet_status'] = [b for b in ntpd_output if 'ja.net' in b][0][0]
status['ntp_janet_checktime'] = list(filter(None, [b for b in ntpd_output if 'ja.net' in b][0].split(' ')))[4]

status['status_time'] = datetime.datetime.now().isoformat()

# Most recent image
imagedir = os.path.expandvars('${HOME}/camera_output')
while True:
    try:
        dirs = os.listdir(imagedir)
        dirs.sort()
        imagedir = os.path.join(imagedir, dirs[-1])
    except NotADirectoryError:
        break
status['recent_image'] = os.path.basename(imagedir)

with open(outputfile, 'w') as f:
    json.dump(status, f)
    f.write('\n')
print('Status written successfully')
