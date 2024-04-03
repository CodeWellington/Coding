#!/usr/bin/bash

OUTPUT=$(Cli -c "show version | inc Serial number")
SN=$(echo $OUTPUT | awk '{print $3}')


tftp IP -c get $SN /mnt/flash/startup-config
