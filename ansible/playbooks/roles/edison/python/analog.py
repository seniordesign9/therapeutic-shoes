"""
Collects analog metrics and sends to influxDB
"""

import argparse
import datetime
import logging
import signal
import time
import urllib2
import collections
from SF_ADC import ADS1x15
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError


METRIC_PREFIX = "edison/"
ADC_INPUTS = 8
Y_INT = 0.7991
SLOPE = 0.3807
rFB = 9710.0
vIn = 3.3


def arg_parse():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port', dest='port', default=8086,
                        help='Sets the influxdb port')
    parser.add_argument('-n', '--hostname', dest='hostname',
                        default='192.168.1.2',
                        help='Sets the influxdb hostname')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='count', default=0,
                        help='Sets the verbosity level')
    parser.add_argument('-t', '--period', dest='period', default=1,
                        help='Sets the period for polling metrics')
    parser.add_argument('-d', '--database', dest='database', default='snap',
                        help='Sets destination database name')
    parser.add_argument('-u', '--user', dest='username', default='admin',
                        help='Sets username for accessing database')
    parser.add_argument('-p', '--password', dest='password', default='admin',
                        help="Sets password for accessing database")
    parser.add_argument('-w', '--wait_time', dest='wait', default=5,
                        help="Sets wait time in between checks")
    parser.add_argument('--timeout', dest='timeout', default=300,
                        help="Sets timeout duration for waits")
    args = parser.parse_args()

    return args


def handler(signum, frame):
    """
    This is a handler to be use for SIGALRM.
    signum (int): Signal number
    frame: current stack frame object or 'None'
    """
    print('Signal handler called with signal', signum)
    raise Exception("Timeout reached")


def update_influx_series(series, metrics, metric_prefix, pin):
    """
    Appends analog metrics to influxDB series. Creates data points
    using the current time and adds tags for pin number.
    Args:
    series (list): series will have points appended to list
    metrics (namedtuple): each metric in the tuple will become data point
    metric_prefix (string): prefix that will be added to each metric name
    pin (string): pin number added as tag
    """
    for i, metric in enumerate(metrics):
        point_values = {
            "time": datetime.datetime.utcnow(),
            "measurement": metric_prefix + metrics._fields[i],
            'fields':  {
                'value': metric,
            },
            'tags': {
                "pinName": pin,
            },
        }
        series.append(point_values)


def wait_for_influx(hostname, port, wait_interval, timeout):
    """
    Blocks until influxDB is available.
    Args:
`   hostname (string): hostname to check
    port (int): port number to check
    wait_interval (int): amount of time in between pings to influx
    timeout (int): Amount of time before waiting stops
    """
    signal.alarm(timeout)  # enable timeout

    # Wait until influxDB is ready
    logging.debug("Inititing wait for influxDB")
    influx_ping = "http://{}:{}/ping".format(hostname, str(port))
    while True:
        time.sleep(wait_interval)
        try:
            res = urllib2.urlopen(influx_ping)
            if res.getcode() == 204:
                break
        except urllib2.URLError:
            pass
    signal.alarm(0)  # disable timeout


def wait_for_database(client, database, wait_interval, timeout):
    """
    Blocks until InfluxDB database is available
    Args:
    client: InfluxDBClient object
    database (string): Database to wait for
    wait_interval (int): Amount of seconds to wait in between queries
    timeout (int): Amount of time before waiting stops
    """
    signal.alarm(timeout)  # enable timeout
    while True:
        try:
            databases = client.get_list_database()
            for db in databases:
                if db['name'] == database:
                    signal.alarm(0)  # disable timeout
                    return
        except InfluxDBClientError as e:
            logging.warning("While waiting for DB, got error: [{}]".format(e))
        time.sleep(wait_interval)


def collect_metrics(args):
    """
    Main loop that collects analog metrics.
    Args:
    args (Namespace object): contains passed in arguments
    """
    series = []
    client = InfluxDBClient(args.hostname, args.port, args.username,
                            args.password, args.database)

    logging.debug("Waiting for database")
    wait_for_database(client, args.database, args.wait, args.timeout)

    # Start collecting metrics
    logging.debug("InfluxDB available. Starting metric collection.")
    adc = collections.namedtuple('adc', 'volts force')
    gain = 4096  # +/- 4.096V
    sps = 250
    adc1 = ADS1x15(0x48)
    adc2 = ADS1x15(0x49)
    while True:
        for num in range(0, ADC_INPUTS):
            if num > 3:
                temp_volts = round(adc1.readADCSingleEnded(num-4, gain, sps)/1000, 6)
            else:
                temp_volts = round(adc2.readADCSingleEnded(num, gain, sps)/1000, 6)

            resistance = (rFB * (vIn / temp_volts)) / 1000000.0
            pounds = (Y_INT + (1 / resistance)) / (SLOPE)
            adc_data = adc(volts=temp_volts, force=pounds)
            update_influx_series(series, adc_data, METRIC_PREFIX, "pin{}".format(num))
            time.sleep(0.001)

        client.write_points(series, time_precision='ms') #time_precision='ms`
        time.sleep(1)


def main(args):
    signal.signal(signal.SIGALRM, handler)

    wait_for_influx(args.hostname, args.port, args.wait, args.timeout)
    collect_metrics(args)


if __name__ == "__main__":
    args = arg_parse()
    verbosity_level = {0: logging.NOTSET,
                       1: logging.INFO,
                       2: logging.WARNING,
                       3: logging.DEBUG,
                       }
    log_level = verbosity_level.get(args.verbose, logging.NOTSET)
    logging.basicConfig(level=logging.NOTSET)
    main(args)
