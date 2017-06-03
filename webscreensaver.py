#!/usr/bin/env python3

# WebScreensaver - Make any web page a screensaver

import os
import sys
import random
import signal
import logging

log = logging.getLogger(__name__)

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkX11', '3.0')
gi.require_version('WebKit', '3.0')
gi.require_version('Soup', '2.4')
from gi.repository import Gtk, Gdk, GdkX11, GObject, Soup, WebKit


class WebScreensaver(object):
    '''
    A simple wrapper for WebKit which works as an XScreensaver Hack
    '''

    def __init__(self, url='http://www.google.com', window_id=None, scripts=None, cookie_file=None, main_queue=None):
        self.window_id = window_id
        self.scripts = scripts
        self.url = url
        self.cookie_file = cookie_file
        self.main_queue = main_queue

        self.w = 640
        self.h = 480

    def setup_window(self):
        '''Perform some magic (if needed) to set up a Gtk window'''
        if self.window_id:
            self.win = Gtk.Window(Gtk.WindowType.POPUP)

            gdk_display = GdkX11.X11Display.get_default()
            self.gdk_win = GdkX11.X11Window.foreign_new_for_display(gdk_display, self.window_id)

            # We show the window so we get a Gdk Window,
            # then we we can reparent it...
            self.win.show()
            self.win.get_window().reparent(self.gdk_win, 0, 0)

            x, y, w, h = self.gdk_win.get_geometry()

            # Make us cover our parent window
            self.win.move(0, 0)
            self.win.set_default_size(w, h)
            self.win.set_size_request(w, h)

            self.w, self.h = w, h
        else:
            self.win = Gtk.Window()
            self.win.set_default_size(self.w, self.h)

    def setup_browser(self):
        '''Sets up WebKit in our window'''
        self.browser = WebKit.WebView()

        # Try to enable webgl
        try:
            settings = self.browser.get_settings()
            settings.set_property('enable-webgl', True)
        except Exception as err:
            log.error("Could not enable WebGL: {}".format(err))

        # Take a stab at guessing whether we are running in the
        # XScreensaver preview window...
        if self.w < 320 and self.h < 240:
            self.browser.set_full_content_zoom(True)
            self.browser.set_zoom_level(0.4)

        self.browser.set_size_request(self.w, self.h)

        self.browser.connect('onload-event', self.handle_on_load)

    def setup_cookie_jar(self):
        if (self.cookie_file):
            cookiejar = Soup.CookieJarText.new(self.cookie_file, False)
            cookiejar.set_accept_policy(Soup.CookieJarAcceptPolicy.ALWAYS)
            session = WebKit.get_default_session()
            session.add_feature(cookiejar)

    def handle_on_load(self, view, frame, user_data=None):
        '''
        Handler for browser page load events.
        This will be executed for every frame within the browser.
        '''

        if not self.scripts:
            return

        for script in self.scripts:
            log.info("Executing script: {}".format(repr(script)))
            self.browser.execute_script(script)

    def setup_layout(self):
        '''Make sure the browser can expand without affecting the window'''
        sw = Gtk.Layout()
        sw.put(self.browser, 0, 0)
        self.win.add(sw)

    def setup(self):
        '''Do all the things!'''
        self.setup_window()
        self.setup_browser()
        self.setup_layout()
        self.setup_cookie_jar()

        def terminate(*args):
            Gtk.main_quit()

        self.win.connect('destroy', terminate)
        self.win.connect('delete-event', terminate)

        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, terminate)

        self.win.show_all()
        Gdk.Window.process_all_updates()

        self.browser.open(self.url)

    @classmethod
    def determine_window_id(cls, win_id=None):
        '''Try and get an XID to use as our parent window'''
        if not win_id:
            win_id = os.getenv('XSCREENSAVER_WINDOW')

        if win_id:
            win_id = int(win_id, 16)

        return win_id




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='WebScreensaver: Run a web page as your screensaver')
    parser.add_argument('-window-id', help='XID of Window to draw on')
    parser.add_argument('-url', help='URL of page to display')
    parser.add_argument('-choose', help='Select a favourite')
    parser.add_argument('-list', action='store_true', help='List favourites')
    parser.add_argument('-cookie-file', metavar='PATH', help='Store cookies in PATH')
    args = parser.parse_args()

    if args.list:
        WebHacks.print_list()
        sys.exit(0)

    url, scripts = None, None

    if args.url:
        url = args.url
    else:
        hack = WebHacks.determine_screensaver(args.choose)
        url, scripts = hack.url, hack.scripts

    saver = WebScreensaver(
        url=url,
        window_id=WebScreensaver.determine_window_id(args.window_id),
        scripts=scripts,
        cookie_file=args.cookie_file
    )
    saver.setup()

    Gtk.main()
