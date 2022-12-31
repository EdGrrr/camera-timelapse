import picamera
from time import sleep, time
from fractions import Fraction
import datetime
import socket
import sys
import numpy as np
from sunposition import sunpos

###################
# Other functions #
###################

def get_lock(process_name):
    # Without holding a reference to our socket somewhere it gets garbage
    # collected when the function exits
    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    print('Testing for exisiting process ... ', end='')
    try:
        # The null byte (\0) means the socket is created 
        # in the abstract namespace instead of being created 
        # on the file system itself.
        # Works only in Linux
        get_lock._lock_socket.bind('\0' + process_name)
        print('None found. Begin timelapse.')
    except socket.error:
        print('Timelapse already running')
        sys.exit()

def wait_until(waittime, mindiff=0.01):
    t = datetime.datetime.utcnow()
    tdiff = (waittime-t).total_seconds()
    if tdiff > mindiff:
        sleep(tdiff)
    return True
    
# This script captures exposures with varying shutter time. 
# The frame rate needs to be longer than the exposure or it won't work. 
# The capture takes as long as the frame rate, so reducing the frame rate saves time for quick exposures.
# Go shortest to longest
#shutter_speeds = [200, 800, 3200]
#ss_label = ['A', 'B', 'C']
shutter_speeds = [200]
ss_label = ['A']

# Site lon, lat, alt r calculating sun position
site_lon, site_lat, site_alt = -0.12, 51.5, 30

# Set the output folder
folder = sys.argv[1]

# Set timelapse prefix
prefix = sys.argv[2]


#Check if timelapse is already running, exit if so
get_lock('timelapse')

now = datetime.datetime.utcnow()
# Run until the next hour
endtime = now + datetime.timedelta(hours=1)
endtime = datetime.datetime(endtime.year, endtime.month,
                            endtime.day, endtime.hour, 0, 0, 0)-datetime.timedelta(seconds=5)

# Check the solar zenith angle
az, sza1 = sunpos(now, site_lat, site_lon, site_alt)[:2]
az, sza2 = sunpos(now+datetime.timedelta(minutes=10), site_lat, site_lon, site_alt)[:2]

if (sza1>95) and (sza2>95):
    # Sun is below horizon.
    # If called within 10 minutes of the hour, record a calibration triplet
    # This makes sure we only get one triplet per hour
    print('Sun below horizon')
    if (now.minute < 10):
        print('Calibration triplet')
        stime = time()
        with picamera.PiCamera(resolution = (1280, 960),
                               framerate=Fraction(1, 6),
                               sensor_mode=3) as camera:
            camera.iso = 800
            camera.annotate_background = picamera.Color('white')
            camera.annotate_foreground = picamera.Color('black')
            camera.annotate_text_size = 12
            camera.shutter_speed = 6000000
            camera.exposure_mode = 'night' # Need to fix gain values somehow!
            camera.awb_mode = 'off'
            camera.awb_gains = (1.73, 1.664)
            for i in range(1, 4):
                # Take a few images, just incase of vehicles etc
                waittime = datetime.datetime.utcnow()
                camera.annotate_text = waittime.strftime('%Y-%m-%d_%H%M%S')
                camera.capture('{}/{}_{}_CAL{}.jpg'.format(folder, prefix, waittime.strftime('%Y-%m-%d_%H%M%S'), i))
    exit()

# Video images are only recorded if daytime
stime = time()
with picamera.PiCamera() as camera:
    print('Setting up camera')
    camera.resolution = (1280, 960)
    stime = time()
    camera.iso = 100 # 100 is lowest valid value

    # Need to set analog and digital gains. Possibly following this?
    # https://gist.github.com/rwb27/a23808e9f4008b48de95692a38ddaa08/
    #camera.exposure_mode = 'off'
    camera.awb_mode = 'cloudy' # should set to constants
    camera.awb_mode = 'off'
    camera.awb_gains = (1.87, 1.531)

    camera.framerate = 30
    camera.annotate_background = picamera.Color('white')
    camera.annotate_foreground = picamera.Color('black')
    camera.annotate_text_size = 12
    
    now = datetime.datetime.utcnow()
    waittime = now + datetime.timedelta(seconds=10)
    waittime = datetime.datetime(waittime.year, waittime.month, waittime.day,
                                 waittime.hour, waittime.minute,
                                 waittime.second-waittime.second%5, 0)
    print('Waiting to start')
    wait_until(waittime)
    print('Begin images')
    while datetime.datetime.utcnow()<endtime:
        for ss, ssl in zip(shutter_speeds, ss_label):  
            camera.shutter_speed = ss
            camera.annotate_text = waittime.strftime('%Y-%m-%d_%H%M%S')
            camera.capture('{}/{}{}.jpg'.format(folder, waittime.strftime('%Y-%m-%d_%H%M%S'), ssl))
            stime = time()

        waittime += datetime.timedelta(seconds=5)
        wait_until(waittime)
