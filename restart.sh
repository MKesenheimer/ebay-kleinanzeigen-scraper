#!/bin/sh

outputdir=/mnt/volumes/usb/ebay-kleinanzeigen-data/

for pidfile in $(ls ${outputdir}/*.id); do
  pid=$(cat $pidfile)
  echo "Killing process with PID $pid..."
  kill -9 $pid
done

echo "Restarting data collector..."
for runfile in $(ls run*.sh); do
  fname=$(basename -- $runfile)
  fname="${fname%.*}" 
  echo "Starting $runfile"
  nohup ./$runfile > ${outputdir}/output-$fname.log 2> ${outputdir}/error-$fname.log &
  sleep 10
done

for pidfile in $(ls ${outputdir}/*.id); do
  pid=$(cat $pidfile)
  echo "New PID is $pid."
done

echo "Done."
