#!/bin/sh

nohup ./watchdog.sh > ${outputdir}/output-watchdog.log 2> ${outputdir}/error-watchdog.log &
