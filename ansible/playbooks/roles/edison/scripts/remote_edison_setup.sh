#!/bin/bash -x 
set -e
temp='date +"%m%d%H%M%Y.%S"'
CURRENT_TIME=$(eval $temp)
ssh root@192.168.1.3 'bash -x' <<COMMANDS
    set -e 
    echo ${CURRENT_TIME}
    date ${CURRENT_TIME}
COMMANDS
