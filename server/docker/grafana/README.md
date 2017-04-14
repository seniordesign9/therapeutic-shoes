# Grafana container
Our anticpated graphing software will be using Grafana.

## Prerequisites
[Install Docker](https://docs.docker.com/engine/installation/)
## Instructions
Build the container: `make`

Starting Grafana:
```
docker run -d -p 3000:3000 --network="influxdb" grafana:team9
```
