FROM grafana/grafana:4.0.0

RUN apt-get update && \
    apt-get install -y curl

COPY dashboards /home/dashboards
COPY entrypoint.sh /entrypoint.sh

EXPOSE 3000
ENTRYPOINT /entrypoint.sh
