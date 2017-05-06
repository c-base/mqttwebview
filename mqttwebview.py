#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import signal
import os
import sys
import webview
import time
import paho.mqtt.client as paho
from random import choice
from threading import Thread
from datetime import datetime
from datetime import timedelta

from config import urls
from config import mqtt_client_id
from config import mqtt_client_name
from config import mqtt_client_password
import config

mqtt_server = "c-beam.cbrp3.c-base.org"
page_timeout = 120

last_change = datetime.now()


def mqtt_connect(client):
    try:
        client.username_pw_set(mqtt_client_name, password=mqtt_client_password)
        if config.mqtt_server_tls:
            print(client.tls_set(config.mqtt_server_cert, cert_reqs=ssl.CERT_OPTIONAL))
            print(client.connect(mqtt_server, port=1884))
        else:
            print(client.connect(mqtt_server))
        client.subscribe("+/+", 1)
        client.on_message = on_message
    except Exception as e: 
        print(e)


def mqtt_loop():
    global last_change
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


def on_message(m, obj, msg):
    global last_change
    print("==> topic %s" % msg.topic)
    if msg.topic == "%s/open" % mqtt_client_name:
        print("===> opening")
        last_change = datetime.now()
        webview.load_url(msg.payload.decode('utf-8'))
        ## TODO os.system('luakit %s' % msg.payload)
    if msg.topic == 'user/boarding':
        last_change = datetime.now()
        try:
            data = json.loads(msg.payload)
            webview.load_ur('https://c-beam.cbrp3.c-base.org/welcome/%s' % data['user'])
        except:
            pass
    else:
        print(msg.payload)


def run_webview_window():
    webview.create_window("It works, Jim!", "http://c-beam.cbrp3.c-base.org/he1display", fullscreen=True)


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    webview.destroy_window()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

Thread(target=run_webview_window).start()
print('Press Ctrl+C to exit')
mqtt_loop()
