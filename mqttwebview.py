#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import signal
import os
import sys
import time
import logging
import json
import uuid
import paho.mqtt.client as paho
import validators
from itertools import cycle
from threading import Thread
import queue
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


from webscreensaver import WebScreensaver
from webhacks import WebHacks
from webscreensaver import Gtk, GLib, GObject

mqtt_server = "c-beam.cbrp3.c-base.org"
page_timeout = 120

last_change = datetime.now() 
last_discovery = datetime.now() - timedelta(seconds=60) # minus 60s so it fires on the first time

log = logging.getLogger(__name__)

important_cycle = cycle(important_urls)
urls_cycle = cycle(urls)

main_queue = queue.Queue()

# A cycle of cycles. Every <page_timeout> minutes the screen will show the next url from the cycle.
# With a configuration like this
#       important_urls = ['c-base.org']
#       urls = ['google.com', 'bing.com']
#       cycle([urls_cycle, important_cycle]
# the result would look like this:
#.      ['google.com', 'c-base.org', 'bing.com', 'c-base.org', 'google.com', ...]
url_list_cycle = cycle([important_cycle, urls_cycle])

stopped = False

class MQTTConnection(object):

    def __init__(self, saver):
        self.saver = saver
        self.client = None
        self.mqtt_client_id = "%s-%s" % (mqtt_client_id, uuid.uuid4())

    def mqtt_connect(self, client):
        try:
            client.username_pw_set(mqtt_client_name, password=mqtt_client_password)
            if config.mqtt_server_tls:
                log.debug(client.tls_set(config.mqtt_server_cert, cert_reqs=ssl.CERT_OPTIONAL))
                log.debug(client.connect(mqtt_server, port=1884))
            else:
                result = client.connect(mqtt_server)
                log.debug("Connect result: %s" % result)
            topic = "%s/open" % mqtt_client_name
            log.info("Subscribing to MQTT topic '%s'" % topic)
            client.subscribe(topic, 1) # level 1 means at least once
            client.on_message = self.on_message
        except Exception as e: 
            log.debug(e)

    def mqtt_loop(self):
        global last_change
        global stopped

        time.sleep(2.0)
        log.info("Starting MQTT loop ...")
        # Set up the signal handler für Ctrl+C
        
        log.debug("MQTT loop started.")
        self.client = paho.Client(self.mqtt_client_id)
        self.mqtt_connect(self.client)
        while stopped == False:
            self.send_discovery_msg(self.client)
            result = self.client.loop(1.0)
            log.debug("loop result is %s" % repr(result))
            if result != 0:
                self.mqtt_connect(self.client)
            if datetime.now() > last_change + timedelta(seconds=page_timeout):
                current_cycle = next(url_list_cycle)
                self.open_url("%s" % next(current_cycle), self.client)
                last_change = datetime.now()
            time.sleep(.5)

    def send_discovery_msg(self, client):
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


    def on_message(self, client, obj, msg):
        global last_change
        log.debug("On message")
        payload = msg.payload.decode('utf-8')
        try:
            url = json.loads(payload)
        except:
            url = payload
        if validators.url(url.split("#", 1)[0]):
            log.debug("Opening %s" % url)
            last_change = datetime.now()
            self.open_url(url, client)
        else:
            log.warning("Malformed URL received: %s" % repr(url))


    def open_url(self, url, client):
        GLib.idle_add(self.saver.open, url)
        client.publish('%s/opened' % mqtt_client_name, url)
        

def signal_handler(signal, frame):
    log.info('You pressed Ctrl+C!')
    sys.exit(0)
    
    
def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def openloop(saver):
    global main_queue
    while stopped == False:
        item = main_queue.get()
        if item == None:
            break
        main_queue.task_done()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='MQTTWebView: Run a web page as screensaver controlled via MQTT')
    parser.add_argument('-window-id', help='XID of Window to draw on')
    parser.add_argument('-url', help='URL of page to display')
    parser.add_argument('-choose', help='Select a favourite')
    parser.add_argument('-list', action='store_true', help='List favourites')
    parser.add_argument('-cookie-file', metavar='PATH', help='Store cookies in PATH')
    args = parser.parse_args()
    
    if args.list:
	    WebHacks.print_list()
	    sys.exit(0)

    setup_logging()
    GObject.threads_init()

    url, scripts = None, None
    wh = WebHacks()
    if args.url:
	    url = args.url
    else:
	    hack = wh.determine_screensaver(args.choose)
	    url, scripts = hack.url, hack.scripts

    saver = WebScreensaver(
        url=url,
        window_id=WebScreensaver.determine_window_id(args.window_id),
        scripts=[],
        cookie_file=args.cookie_file,
    )
    saver.setup()
   
    conn = MQTTConnection(saver=saver) 
    mqtt_thread = Thread(target=conn.mqtt_loop)
    mqtt_thread.start()
    
    Gtk.main()


    stopped = True
