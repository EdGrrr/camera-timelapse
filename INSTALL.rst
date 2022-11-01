Installation/setup of a timelapse camera
========================================

Files
-----

The required files for setting up a timelapse system are in the `Timelapse` folder. The current design has a cron job calling `Timelapse/camera.sh` every 10 minutes. The job can be setup to run either more or less often. More often may produce extra calibration triplets at night, less often and you have to wait longer for things to start up again after a restart.

`Timelapse/config.sh` - contains variables that will change between cameras. If you are only using one camera, you can leave this as-is

`Timelapse/multi_exposure_calibrate.py` - the python code that actually runs the camera. Can record images at multiple different exposures, adding suffixes as required. Takes 'calibration' (long exposure images) at night that can be used to get an accurate direction for the camera (if the starfield is known).

`Timelapse/pic_to_vid.sh` - Converts a folder of images to an mp4 video. Designed to run once an hour (cron job), converts the images from the previous hour.

`Timelapse/sunposition.py` - utility functions for calculating daylight/nighttime


Notes
-----

From previous experience, raspberry pis sometime get stuck in a situation where they are unable to access the camera. A nightly restart appears to fix this (and I have had no issues since introducing the lockfile test for already running code). You may want to have a nightly restart cron job anyway,

You may want to write to an external USB drive, rather than the micro SD card. Some of our cameras have developed issues that may be related to sd card corruption.

For synchronising multiple cameras, accurate time is essential. NTP seems accurate enough for most cases, but obviously depends on network connection.
