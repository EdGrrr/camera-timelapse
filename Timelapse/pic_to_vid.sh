#! /bin/bash

SOURCE=$( readlink -f -- "$0"; )
SCRIPT_DIR=$( dirname -- "$SOURCE"; )

. ${SCRIPT_DIR}/config.sh

DAY=$(date -u -d '1 hour ago' +"%Y-%m-%d")
HOUR=$(date -u -d '1 hour ago' +"%H")

FOLDER=${MAIN_FOLDER}/${DAY}/${HOUR}
mkdir -p ${MAIN_FOLDER}/cal/${DAY}
mkdir -p ${MAIN_FOLDER}/videos/${DAY}


cd ${FOLDER}
mv *.mp4 ${MAIN_FOLDER}/videos/${DAY} 2> /dev/null
mv *_CAL*.jpg ${MAIN_FOLDER}/cal/${DAY} 2> /dev/null

cd ..
# tar -zcvf ${HOUR}.tar.gz ${HOUR} 
rm -rf ${HOUR}
