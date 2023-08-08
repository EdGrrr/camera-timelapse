#! /bin/bash

SOURCE=$( readlink -f -- "$0"; )
SCRIPT_DIR=$( dirname -- "$SOURCE"; )

. ${SCRIPT_DIR}/config.sh

# Move calibration images first, picking up any old images
DAY=$(date -u -d '1 hour ago' +"%Y-%m-%d")
mkdir -p ${MAIN_FOLDER}/cal/${DAY}
cd ${MAIN_FOLDER}
for i in 2*/*/*CAL*.jpg;
do
    # Skip non-matching glob case
    # https://stackoverflow.com/questions/20796200/how-to-loop-over-files-in-directory-and-change-path-and-add-suffix-to-filename
    [ -e "$i" ] || continue;
    mv $i cal/$(echo $i | cut -d "/" -f 1);
done

# Now move the previous video
HOUR=$(date -u -d '1 hour ago' +"%H")
FOLDER=${MAIN_FOLDER}/${DAY}/${HOUR}
mkdir -p ${MAIN_FOLDER}/videos/${DAY}

cd ${FOLDER}
mv *.mp4 ${MAIN_FOLDER}/videos/${DAY} 2> /dev/null
mv *_CAL*.jpg ${MAIN_FOLDER}/cal/${DAY} 2> /dev/null

cd ..
# tar -zcvf ${HOUR}.tar.gz ${HOUR} 
rm -rf ${HOUR}


