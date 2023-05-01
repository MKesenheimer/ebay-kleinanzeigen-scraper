#!/bin/sh

outputdir=/mnt/volumes/usb/ebay-kleinanzeigen-data/
nohup ./watchdog.sh > ${outputdir}/output-watchdog.log 2> ${outputdir}/error-watchdog.log &
