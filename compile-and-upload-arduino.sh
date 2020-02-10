#!/bin/bash
NAME=arduino-shaker-server
FBQN=arduino:megaavr:nona4809
DEVICE=/dev/ttyACM0
arduino-cli compile --fqbn $FBQN $NAME
if [ $? -ne 0 ]; then
    echo "compile error, exit here"
    exit
fi
arduino-cli upload -v -p $DEVICE --fqbn $FBQN $NAME

# minicom -b 9600 -o -D /dev/serial/by-id/usb-Arduino_LLC_Arduino_Nano_Every_6EB94DED51514743594A2020FF06191B-if00
