#! /bin/bash

SOURCE=$( readlink -f -- "$0"; )
SCRIPT_DIR=$( dirname -- "$SOURCE"; )

. ${SCRIPT_DIR}/config.sh

DATE=$(date -u +"%Y-%m-%d_%H%M")
DAY=$(date -u +"%Y-%m-%d")
HOUR=$(date -u +"%H")
FOLDER=${MAIN_FOLDER}/gcal/

mkdir -p ${FOLDER}

# Have to stop the camera timelapse service (if it is running)
sudo systemctl stop argus-camera-timelapse.service
python3 ${SCRIPT_DIR}/calibration_images.py ${FOLDER} ${PREFIX}

# Restart the camera timelapse service - this could result in an extra set of
# nighttime calibration images (although that is rare)
sudo systemctl start argus-camera-timelapse.service
