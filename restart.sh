#!/bin/sh

outputdir=/mnt/volumes/usb/ebay-kleinanzeigen-data/

pid=$(cat ${outputdir}/process.id)
echo "Killing process with PID $pid..."
kill -9 $pid

echo "Restarting data collector..."
nohup ./run.sh > ${outputdir}/output.log 2> ${outputdir}/error.log &
sleep 10

pid=$(cat ${outputdir}/process.id)
echo "New PID is $pid."
echo "Done."