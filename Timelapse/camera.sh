#! /bin/bash

SOURCE=$( readlink -f -- "$0"; )
SCRIPT_DIR=$( dirname -- "$SOURCE"; )

. ${SCRIPT_DIR}/config.sh

# Takes up to an hour worth of images. Should automatically timeout at the hour

DATE=$(date -u +"%Y-%m-%d_%H%M")
DAY=$(date -u +"%Y-%m-%d")
HOUR=$(date -u +"%H")
FOLDER=${MAIN_FOLDER}/${DAY}/${HOUR}

mkdir -p ${FOLDER}
python3 ${SCRIPT_DIR}/multi_exposure_calibrate.py ${FOLDER} ${PREFIX} ${SCRIPT_DIR}/../config.json
