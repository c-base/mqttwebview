#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import signal
import os
import sys
import webview
import time
import logging
import json
import paho.mqtt.client as paho
import validators
from itertools import cycle
from threading import Thread
from datetime import datetime
from datetime import timedelta
from logging.handlers import RotatingFileHandler

from config import urls
from config import important_urls
from config import mqtt_client_id
from config import mqtt_client_name
from config import mqtt_client_password
from config import discovery_message

import config
mqtt_server = "c-beam.cbrp3.c-base.org"
page_timeout = 120

last_change = datetime.now() 
last_discovery = datetime.now() - timedelta(seconds=60) # minus 60s so it fires on the first time

log = logging.getLogger(__name__)

important_cycle = cycle(important_urls)
urls_cycle = cycle(urls)

# A cycle of cycles. Every <page_timeout> minutes the screen will show the next url from the cycle.
# With a configuration like this
#       important_urls = ['c-base.org']
#       urls = ['google.com', 'bing.com']
#       cycle([urls_cycle, important_cycle]
# the result would look like this:
#.      ['google.com', 'c-base.org', 'bing.com', 'c-base.org', 'google.com', ...]
url_list_cycle = cycle([important_cycle, urls_cycle])


def mqtt_connect(client):
    try:
        client.username_pw_set(mqtt_client_name, password=mqtt_client_password)
        if config.mqtt_server_tls:
            log.debug(client.tls_set(config.mqtt_server_cert, cert_reqs=ssl.CERT_OPTIONAL))
            log.debug(client.connect(mqtt_server, port=1884))
        else:
            log.debug(client.connect(mqtt_server))
        client.subscribe("%s/open" % mqtt_client_name, 1) # level 1 means at least once
        client.on_message = on_message
    except Exception as e: 
        log.debug(e)

def mqtt_loop():
    global last_change

    time.sleep(2.0)
    log.info("Starting MQTT loop ...")
    # Set up the signal handler für Ctrl+C
    
    log.debug("MQTT loop started.")
    client = paho.Client(mqtt_client_id)
    mqtt_connect(client)
    while True:
        send_discovery_msg(client)
        result = client.loop(1)
        if result != 0:
            mqtt_connect(client)
        time.sleep(0.5)
        if datetime.now() > last_change + timedelta(seconds=page_timeout):
            current_cycle = next(url_list_cycle)
            open_url("%s" % next(current_cycle), client)
            last_change = datetime.now()


def send_discovery_msg(client):
    """
    Send the discovery message, such that MsgFlo can automatically set up a component
    whenever a new instance of this program is run.
    
    Details, see: https://github.com/c-base/mqttwebview/issues/2
    """
    global last_discovery
    passed = datetime.now() - last_discovery
    if passed.seconds > 59:
        log.debug("Sending discovery message ...")
        client.publish('fbp', payload=json.dumps(discovery_message).encode('utf-8'), qos=0)
        last_discovery = datetime.now()


def on_message(client, obj, msg):
    global last_change
    payload = msg.payload.decode('utf-8')
    try:
        url = json.loads(payload)
    except:
        url = payload
    if validators.url(url.split("#", 1)[0]):
        log.debug("Received message, opening %s" % url)
        last_change = datetime.now()
        open_url(url, client)
    else:
        log.warning("Malformed URL received: %s" % repr(url))


def open_url(url, client):
    webview.load_url(url)
    client.publish('%s/opened' % mqtt_client_name, url)
	

def run_webview_window():
    # Will block here until window is closed.
    current_cycle = next(url_list_cycle)
    webview.create_window("mqttwebview", next(current_cycle), fullscreen=False)


def signal_handler(signal, frame):
    log.info('You pressed Ctrl+C!')
    webview.destroy_window()
    sys.exit(0)
    
    
def main():
    # Set up logging in a autorotation logfile in the same directory as this file.
    logfilename = os.path.realpath(os.path.join(os.path.dirname(__file__), 'debug.log'))
    handler = RotatingFileHandler(logfilename, maxBytes=5242880, backupCount=1) 
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(format)
    log.addHandler(handler)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    # use this to change the log-level
    log.setLevel(logging.DEBUG)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the thread
    t2 = Thread(target=mqtt_loop)
    t2.start()
    #t1 = Thread(target=run_webview_window)
    run_webview_window()
    
    
    print('Press Ctrl+C to exit')
    # Go and listen to mqtt.
        
if __name__ == '__main__':
    main()
