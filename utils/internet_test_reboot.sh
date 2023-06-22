#!/bin/bash

echo -e "GET http://argus.edgryspeerdt.com/ HTTP/1.0\n\n" | nc argus.edgryspeerdt.com 80 > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "Online"
else
    echo "Offline, rebooting"
    shutdown -r +1
fi
