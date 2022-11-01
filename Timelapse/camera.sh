#! /bin/bash

. /home/pi/Timelapse/config.sh

# Takes up to an hour worth of images. Should automatically timeout at the hour

DATE=$(date -u +"%Y-%m-%d_%H%M")
DAY=$(date -u +"%Y-%m-%d")
HOUR=$(date -u +"%H")
FOLDER=${MAIN_FOLDER}/${DAY}/${HOUR}

mkdir -p ${FOLDER}
python3 /home/pi/Timelapse/multi_exposure_calibrate.py ${FOLDER} ${PREFIX}
