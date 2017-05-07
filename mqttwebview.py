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
from random import choice
from threading import Thread
from datetime import datetime
from datetime import timedelta
from logging.handlers import RotatingFileHandler

from config import urls
from config import mqtt_client_id
from config import mqtt_client_name
from config import mqtt_client_password
import config

mqtt_server = "c-beam.cbrp3.c-base.org"
page_timeout = 120

last_change = datetime.now()

log = logging.getLogger(__name__)

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
        log.debig(e)


def mqtt_loop():
    global last_change
    time.sleep(5.0)
    log.debug("MQTT loop started.")
    client = paho.Client(mqtt_client_id)
    mqtt_connect(client)
    while True:
        result = client.loop(1)
        if result != 0:
            mqtt_connect(client)
        time.sleep(0.5)
        if datetime.now() > last_change + timedelta(seconds=page_timeout):
            webview.load_url("%s" % choice(urls))
            last_change = datetime.now()


def on_message(client, obj, msg):
    global last_change
    payload = msg.payload.decode('utf-8')
    try:
        url = json.loads(payload)
    except json.decoder.JSONDecodeError:
        url = payload
    last_change = datetime.now()
    if validators.url(url):
        log.debug("Received message, opening %s" % url)
        webview.load_url(url)
        client.publish('%s/opened' % mqtt_client_name, url)
    else:
        log.warning("Malformed URL received: '%s'" % repr(url))


def run_webview_window():
    # Will block here until window is closed.
    webview.create_window("It works, Jim!", "http://c-beam.cbrp3.c-base.org/he1display", fullscreen=True)
    sys.exit(1)


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
    
    # Set up the signal handler für Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Start the thread
    Thread(target=run_webview_window).start()
    mqtt_loop()
    
    print('Press Ctrl+C to exit')
    # Go and listen to mqtt.
        
if __name__ == '__main__':
    main()
