#!/usr/bin/bash

#filter by serial number
OUTPUT=$(Cli -c "show version | inc Serial number")
SN=$(echo $OUTPUT | awk '{print $3}')

#replace IP with the FTP server IP
tftp IP -c get $SN /mnt/flash/startup-config
#You must have a configuration file named with the serial number
