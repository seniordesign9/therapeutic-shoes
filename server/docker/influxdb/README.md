## InfluxDB container
This container holds the anticipated database for the project.
## Prerequisites
[Install Docker](https://docs.docker.com/engine/installation/)
## Instructions
Build the container: `make`

Start the database:
```
docker run docker run -d -p 8086:8086 -p 8083:8083 -v $DIR:/var/lib/influxdb --network="influxdb" influxdb
```
Replace $DIR with the directory in which data should be stored.

