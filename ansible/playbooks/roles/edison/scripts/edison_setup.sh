#!/bin/bash -x
set -e 
SNAP_PLUGINS_PATH=$PWD/plugins
SNAP_TASK_PATH=$PWD/tasks/task.json
LOG_LEVEL=3
AUTO_START=${AUTO_START:-false}

echo "Starting Influxdb server" && \
influxd 2>/dev/null &
sleep 5

echo "Creating Snap database" && \
influx <<COMMANDS
    create database snap
COMMANDS

echo "Starting Snap daemon" && \
snapd -l $LOG_LEVEL -t 0 --plugin-load-timeout 60 &
sleep 5
echo "Loading plugins" && \
snapctl plugin load  ${SNAP_PLUGINS_PATH}/snap-plugin-processor-passthru && \
snapctl plugin load  ${SNAP_PLUGINS_PATH}/snap-plugin-collector-analog && \
snapctl plugin load  ${SNAP_PLUGINS_PATH}/snap-plugin-publisher-influxdb && \
sleep 1

echo "Creating Snap task" 
if $AUTO_START 
then
    snapctl task create -t ${SNAP_TASK_PATH}
else
    snapctl task create --no-start -t ${SNAP_TASK_PATH}
fi
