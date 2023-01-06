#! /bin/python3

import os
import re
import subprocess
import json
import datetime
import sys
import sensors

def get_process_output(proc):
    process = subprocess.Popen(proc, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    return output

try:
    outputfile = sys.argv[1]
except:
    outputfile = 'status.json'


status = {}

# Most recent image
try:
    imagedir = os.path.expandvars('${HOME}/camera_output')
    while True:
        try:
            dirs = os.listdir(imagedir)
            dirs.sort()
            if 'cal' in dirs: dirs.remove('cal')
            if 'videos' in dirs: dirs.remove('videos')
            if len(dirs) == 0:
                # No valid image directories
                status['recent_image'] = None
                break
            imagedir = os.path.join(imagedir, dirs[-1])
        except NotADirectoryError:
            status['recent_image'] = os.path.basename(imagedir)
            break
except FileNotFoundError:
    # No USB storage
    status['recent_image'] = None
    
# Do now to avoid GPS issues with timing of status
status['status_time'] = datetime.datetime.now().isoformat()

# Freespace
df_output = get_process_output(['df', '-h'])
try:
    df_usb = [b for b in
              [ a for a in df_output.decode('ascii').split('\n')
                if 'USB' in a][0].split(' ')
              if b != '']
    status['freespace'] = df_usb[3]
except IndexError:
    status['freespace'] = None
    
df_output = get_process_output(['df'])
try:
    df_usb = [b for b in
              [ a for a in df_output.decode('ascii').split('\n')
                if 'USB' in a][0].split(' ')
              if b != '']
    status['usb_usage'] = f'{100*float(df_usb[2])/float(df_usb[1]):.3f}%'
except IndexError:
    status['usb_usage'] = None

    
# Timelapse status
timelapse_running = [b for b in
                     get_process_output(['systemctl', 'show', 'argus-camera-timelapse']).decode('ascii').split('\n')
                     if b.startswith('ActiveState=')][0].split('=')[1]
status['timelapse_status'] = timelapse_running
timelapse_timer = [b for b in
                   get_process_output(['systemctl', 'show', 'argus-camera-timelapse.timer']).decode('ascii').split('\n')
                   if b.startswith('ActiveState=')][0].split('=')[1]
status['timelapse_timer'] = timelapse_timer


# GPS status
gps_output = get_process_output(['gpspipe', '-w', '-n 10']).decode('ascii')
x  = re.search("mode\":(.),.*lat\":(\d*.\d*),.*lon\":(.*?\..*?),.*altHAE\":(.*?\..*?),.*altMSL\":(.*?\..*?),", gps_output)
try:
    status['gps_status'] = x.groups()[0]
except:
    status['gps_status'] = None
try:
    status['gps_lon'] = x.groups()[2]
    status['gps_lat'] = x.groups()[1]
    status['gps_altHAE'] = x.groups()[3]
    status['gps_altMSL'] = x.groups()[4]

except:
    status['gps_lon'] = None
    status['gps_lat'] = None
    status['gps_altHAE'] = None
    status['gps_altMSL'] = None

# NTP status
ntpd_output = get_process_output(['ntpq', '-p']).decode('ascii').split('\n')
status['ntp_pps_status'] = [b for b in ntpd_output if 'PPS' in b][0][0]
status['ntp_pps_checktime'] = list(filter(None, [b for b in ntpd_output if 'PPS' in b][0].split(' ')))[4]
status['ntp_gps_status'] = [b for b in ntpd_output if 'GPS' in b][0][0]
status['ntp_janet_status'] = [b for b in ntpd_output if 'ja.net' in b][0][0]
status['ntp_janet_checktime'] = list(filter(None, [b for b in ntpd_output if 'ja.net' in b][0].split(' ')))[4]

try:
    # Sensors
    press = sensors.Pressure()
    pd = press.get_data()
    status.update(pd)

    acc = sensors.AccelGyro()
    acd = acc.get_data()
    status.update(acd)

    mag = sensors.Mag()
    md = mag.get_data()
    status.update(md)
    
    status['accXangle'], status['accYangle'] = sensors.get_rotation_angles(acd)
    status['heading'] = sensors.get_heading(md)
    status['tiltCompHeading'], status['pitch'], status['roll'] = sensors.tilt_compensated_heading(acd, md)
except OSError:
    print('Sensors unavailable via I2C')

status['rpi_temp'] = get_process_output(['vcgencmd', 'measure_temp']).decode('ascii').strip()[5:-2]
    
with open(outputfile, 'w') as f:
    json.dump(status, f)
    f.write('\n')
print('Status written successfully')
