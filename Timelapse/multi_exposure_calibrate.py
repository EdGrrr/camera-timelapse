import picamera2
from time import sleep, time
from PIL import Image
import datetime
import socket
import sys
import numpy as np
from sunposition import sunpos
import json
import os

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
assert(len(shutter_speeds) == 1)

ss_label = ['A']

# Size of the timestamp label
ts_factor = 4

# Set the output folder
folder = sys.argv[1]

# Set timelapse prefix
prefix = sys.argv[2]

# Get the config file
config_file = sys.argv[3]
with open(sys.argv[3]) as f:
    config = json.load(f)

# Site lon, lat, alt r calculating sun position
site_lon, site_lat, site_alt = config['site_lon_degE'], config['site_lat_degN'], config['site_alt_m']

#Check if timelapse is already running, exit if so
get_lock('timelapse')

# Is the time likely correct?
# I2C must be started to get RTC
while not os.path.exists('/dev/i2c-1'):
    sleep(1)

now = datetime.datetime.utcnow()
# Run until the next hour
endtime = now + datetime.timedelta(hours=1)
endtime = datetime.datetime(endtime.year, endtime.month,
                            endtime.day, endtime.hour, 0, 0, 0)-datetime.timedelta(seconds=10)

# Check the solar zenith angle
az, sza1 = sunpos(now, site_lat, site_lon, site_alt)[:2]
az, sza2 = sunpos(now+datetime.timedelta(minutes=10), site_lat, site_lon, site_alt)[:2]

if (sza1>config['sza_daylight_limit_deg']) and (sza2>config['sza_daylight_limit_deg']):
    # Sun is below horizon.
    # If called within 10 minutes of the hour, record a calibration triplet
    # This makes sure we only get one triplet per hour
    print('Sun below horizon')
    if (now.minute < 10) or (config['hourly_night_views']==False) or (config['power_manage']):
        if config['camera_heater']:
            print('Heating camera')
            stime = time()
            # with picamera.PiCamera(resolution=(1280,720),
            #                        framerate=180,
            #                        sensor_mode=6) as camera:
            #     stream = picamera.PiCameraCircularIO(camera, seconds=1)
            #     camera.start_recording(stream, format="mjpeg")

            #     while True:
            #         camera.wait_recording(1)
            #         if time() > stime+config['camera_heater_time']:
            #             break

        print('Calibration triplet')
        stime = time()
        with picamera2.Picamera2() as camera:
            camera.configure(
                camera.create_still_configuration(
                    queue=False,
                    display=None,  # No preview window
                    main={'size': config['resolution']}
                ))
            camera.set_controls({'ExposureTime': 6000000,
                                 'AeEanble': False,
                                 'AnalogueGain': 8.0, # AG is approximately ISO/100
                                 'AwbEnable': False,  # Turn off AWB
                                 'ColourGains': config['white_balance'],
                                 })
            camera.start()
            # Wait for camera to start
            sleep(2)

            for i in range(1, 4):
                request = camera.capture_request()
                data = request.make_array('main')
                metadata = request.get_metadata()
                request.release()

                # Timestamp
                stamp = int(time())
                ts_array = np.array(list(np.binary_repr(stamp))).astype('int')
                ts_array = ts_array[None, :].repeat(ts_factor, axis=1).repeat(ts_factor, axis=0)
                data[:ts_factor, :(31*ts_factor), :] = 255*ts_array[:, :, None]

                im = Image.fromarray(data)
                waittime = datetime.datetime.utcnow()
                im.save'{}/{}_{}_CAL{}.jpg'.format(folder, prefix, waittime.strftime('%Y-%m-%d_%H%M%S'), i))

    if config['power_manage']:
        # Run shutdown commands here
        import pijuice
        import os
        import datetime
        import time

        pj = pijuice.PiJuice(1, 0x14)

        # Ensure there is a PiJuice attached, otherwise the shutdown is fatal!
        if pj.status.GetStatus()['error'] != 'NO_ERROR':
            raise IOError('PiJuice cannot be contacted')

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

        pj.rtcAlarm.ClearAlarmFlag()
        if config['hourly_night_views']:
            # Wakeup at 57 min to hour
            wakeupmin = 57
        else:
            # Wakeup at 7 minutes to 10 minute intervals
            wakeupmin = (((t.minute+4)//10)*10+7)%60
        pj.rtcAlarm.SetAlarm({'year': 'EVERY_YEAR',
                              'month': 'EVERY_MONTH',
                              'day': 'EVERY_DAY',
                              'hour': 'EVERY_HOUR',
                              'minute': wakeupmin})

        pj.rtcAlarm.SetWakeupEnabled(True)

        # Remove power to PiJuice MCU IO pins
        pj.power.SetSystemPowerSwitch(0)

        # Remove 5V power to RPi after 20 seconds
        pj.power.SetPowerOff(20)

        print(pj.rtcAlarm.GetAlarm())
        # Shut down the RPi
        os.system(f"sudo shutdown -h now 'Restarting at {wakeupmin}'")

    exit()

# Video images are only recorded if daytime
import cv2 # This is slow so only if we need it

stime = time()
with picamera2.PiCamera2() as camera:
    print('Setting up camera')
    camera.configure(
        camera.create_still_configuration(
            queue=False,   # Only get a frame when it is requested
            display=None,  # No preview window
            main={'size': config['resolution']}
        ))
    camera.set_controls({'ExposureTime': shutter_speeds[0],
                         'AeEanble': False,
                         'AnalogueGain': 1.0, # AG is approximately ISO/100
                         'AwbEnable': False,  # Turn off AWB
                         'ColourGains': config['white_balance'],
                         })
    camera.start()
    
    stime = time()

    now = datetime.datetime.utcnow()
    waittime = now + datetime.timedelta(seconds=10)
    waittime = datetime.datetime(waittime.year, waittime.month, waittime.day,
                                 waittime.hour, waittime.minute,
                                 waittime.second-waittime.second%5, 0)

    videos = {}
    for ssl in ss_label:
        video_name = f"{folder}/{prefix}_{waittime.strftime('%Y%m%d_%H%M%S')}_{ssl}.mp4"
        videos[ssl] = cv2.VideoWriter(video_name, cv2.VideoWriter.fourcc(*'mp4v'), 25, tuple(config['resolution']))

    print('Waiting to start')
    wait_until(waittime)
    print('Begin images')
    while datetime.datetime.utcnow()<endtime:
        for ss, ssl in zip(shutter_speeds, ss_label):
            # camera.shutter_speed = ss
            # camera.annotate_text = waittime.strftime('%Y-%m-%d_%H%M%S')
            img_filename = '{}/{}{}.jpg'.format(folder, waittime.strftime('%Y-%m-%d_%H%M%S'), ssl)

            request = camera.capture_request()
            data = request.make_array('main')
            metadata = request.get_metadata()
            request.release()

            # Timestamp
            stamp = int(time())
            ts_array = np.array(list(np.binary_repr(stamp))).astype('int')
            ts_array = ts_array[None, :].repeat(ts_factor, axis=1).repeat(ts_factor, axis=0)
            data[:ts_factor, :(31*ts_factor), :] = 255*ts_array[:, :, None]

            videos[ssl].write(data)
            stime = time()

        waittime += datetime.timedelta(seconds=config['image_timedelta_seconds'])
        wait_until(waittime)

    print('Closedown videos')
    cv2.destroyAllWindows()
    for ssl in ss_label:
        videos[ssl].release()
