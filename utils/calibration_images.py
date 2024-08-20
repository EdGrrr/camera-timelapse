import picamera2
from time import sleep, time
from PIL import Image
import datetime
import socket
import sys
import numpy as np
import json
import os

###################
# Other functions #
###################

        
def wait_until(waittime, mindiff=0.01):
    t = datetime.datetime.utcnow()
    tdiff = (waittime-t).total_seconds()
    if tdiff > mindiff:
        sleep(tdiff)
    return True


def timestamp_image(tstamp, data, ts_factor, exposure=None):
    stamp = int(tstamp)
    ts_array = np.array(list(np.binary_repr(stamp, 31))).astype('int')
    ts_array = ts_array[None, :].repeat(ts_factor, axis=1).repeat(ts_factor, axis=0)
    data[:ts_factor, :(31*ts_factor), :] = 255*ts_array[:, :, None]
    if exposure is not None:
        stamp = int(exposure)
        ts_array = np.array(list(np.binary_repr(stamp, 31))).astype('int')
        ts_array = ts_array[None, :].repeat(ts_factor, axis=1).repeat(ts_factor, axis=0)
        data[ts_factor:(2*ts_factor), :(31*ts_factor), :] = 255*ts_array[:, :, None]
    return data


def update_latest(filename, latest_location):
    with open(latest_location, 'w') as f:
        f.write(filename+'\n')
    f.close()


def thumbnail_create(data, output_filename, max_dim=100):
    im = Image.fromarray(data)
    ratio = im.size[1]/im.size[0]
    tbsize = max_dim, int(ratio*max_dim)
    im.thumbnail(tbsize)
    im.save(output_filename)


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


print('Calibration images')
stime = datetime.datetime.utcnow()
try:
    with picamera2.Picamera2() as camera:
        camera.configure(
            camera.create_still_configuration(
                queue=False,
                display=None,  # No preview window
                main={'size': config['resolution']}
            ))
        camera.start()
        # Wait for camera to start
        sleep(2)

        for i in range(1, 10):
            print('Request capture', end='', flush=True)
            request = camera.capture_request()
            data = request.make_array('main')
            print(' - Capture complete', flush=True)
            metadata = request.get_metadata()
            request.release()

            # Timestamp
            data = timestamp_image(time(), data, ts_factor, exposure=metadata['DigitalGain']*metadata['ExposureTime'])

            im = Image.fromarray(data)
            waittime = datetime.datetime.utcnow()
            im.save(f"{folder}/{prefix}_{stime.strftime('%Y%m%dT%H%M%S')}_GCAL{i:0>2}.jpg")
except:
    # FIX: Stop camera running all night
    pass
