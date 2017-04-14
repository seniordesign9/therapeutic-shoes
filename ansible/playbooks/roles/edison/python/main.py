
from Spark_ADC import Adc
from config import *
import os
import time
import mraa
import logging

ain0_operational_status = 0b0
ain0_input_multiplexer_configuration = 0b111
ain0_programmable_gain_amplifier_configuration = 0b001
ain0_device_operating_mode = 0b0
ain0_data_rate = 0b100
ain0_comparator_mode = 0b0
ain0_compulator_polarity = 0b0
ain0_latching_comparator = 0b0
ain0_comparator_queue_and_disable = 0b11

pin_GPLOW13 = 14

pt1 = Adc(address=0x48)
pt1.set_config_command(ain0_operational_status, ain0_input_multiplexer_configuration,
                       ain0_programmable_gain_amplifier_configuration,
                       ain0_device_operating_mode, ain0_data_rate, ain0_comparator_mode, ain0_compulator_polarity,
                       ain0_latching_comparator, ain0_comparator_queue_and_disable)

def send_mail():
	import smtplib
	from email.MIMEMultipart import MIMEMultipart
	from email.MIMEText import MIMEText
 
 
	fromaddr = "ahribeng@gmail.com"
	toaddr = "ahribeng@gmail.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "LOW BATTERY ... PLEASE RECHARGE"
	 
	body = "OOPS your battery seems to be low please recharge"
	msg.attach(MIMEText(body, 'plain'))
 
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, 'snolie 4 life')
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()

def calcVolt():
    adc_value = pt1.adc_read()
    VOUT2 = (adc_value)/1000.0 
    VOUT = VOUT2 * (R2 + R1)/R2
    print (VOUT)
    return VOUT


LOW = 0
HIGH = 0
SHUTDOWN = 0
SLEEP = 1
VOUT = 0

logging.basicConfig(filename='volt.log',level=logging.DEBUG)
logging.info('Voltage Log')

while True:
    logging.info('Sampling Voltage')	
    for index in range(15):
        time.sleep(2)
        VOUT += calcVolt()
        logging.info('Pass # {0} Cumulative Voltage {1}'.format(index + 1, VOUT))
    VOUT = VOUT / 15.0
    logging.info('VOUT / 15: {}'.format(VOUT))
    if (VOUT > LOWBATTERY):
        if (HIGH == 0):
            HIGH = 1
            LOW = 0
            SHUTDOWN = 0
            SLEEP = 30.0
    elif (VOUT <= LOWBATTERY and VOUT > SHTBATTERY):
        if (LOW == 0):
            HIGH = 0
            LOW = 1
            SHUTDOWN = 0
            SLEEP = 5
	#send_mail()
	time.sleep(1)
    elif (VOUT <= SHTBATTERY):
        if (SHUTDOWN == 0):
            HIGH = 0
            LOW = 0
            SHUTDOWN = 1
    if (SHUTDOWN):
	logging.info("System Shutting down : Voltage: {}".format(VOUT))
        os.system("shutdown now -h")
    time.sleep(15 * SLEEP)
    VOUT = 0
