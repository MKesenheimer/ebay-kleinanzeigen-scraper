#!/bin/sh

outputdir=/mnt/volumes/usb/ebay-kleinanzeigen-data/

for pidfile in $(ls ${outputdir}/*.id); do
  pid=$(cat $pidfile)
  echo "Killing process with PID $pid..."
  kill -9 $pid
done

echo "Done."
