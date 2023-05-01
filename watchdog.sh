#!/bin/bash

ncheck=$(ls run* | wc -l)

while :
do
  nproc=$(($(ps aux | grep ekscraper | wc -l) - 1))
  echo Number of running processes: $nproc
  echo Number of processes that should run: $ncheck
  if [ "$ncheck" -gt "$nproc" ]; then
    echo "Restarting processes..."
    sh ./restart.sh
  else
    echo "Ok."
  fi
  sleep 86400
done

