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
# for LABEL in A;
# do
#     if compgen -G "*${LABEL}.jpg" > /dev/null; then
#         ffmpeg -hide_banner -loglevel error -framerate 25 -pattern_type glob -i '*'"${LABEL}"'.jpg' -c:v libx264 -crf 18 -preset slow "${MAIN_FOLDER}"/videos/"${DAY}"/"${PREFIX}"_"${DAY}"_"${HOUR}${LABEL}".mp4;
#     fi
# done
mv *_CAL*.jpg ${MAIN_FOLDER}/cal/${DAY} 2> /dev/null

cd ..
tar -zcvf ${HOUR}.tar.gz ${HOUR} 
rm -rf ${HOUR}
