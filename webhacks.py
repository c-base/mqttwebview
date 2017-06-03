# -*- coding: utf-8 -*-
import itertools

class UserScripts(object):
    '''
    Some quick and dirty scripts to help us remove cruft from web pages
     '''

    @classmethod
    def remove_ids(cls, _id):
        script = '''
            (function() {
                var el = document.getElementById("%s");
                if (el) {
                    el.parentNode.removeChild(el);
                }
            })();
        '''
        return script % _id

    @classmethod
    def remove_tags(cls, tag):
        script = '''
            (function() {
                var tags = document.getElementsByTagName("%s");
                if (tags && tags.length > 0) {
                    for (var i = 0; i < tags.length; i++) {
                        var el = tags[i];
                        el.parentNode.removeChild(el);
                    }
                }
            })();
        '''
        return script % tag


class Hack(object):
    __slots__ = "name url scripts".split(" ")
    def __init__(self, name, url=None, scripts=None):
        self.name, self.url, self.scripts = name, url, scripts

class WebHacks(object):
    '''
    A collection of neat HTML5/WebGL demos
    '''
    
    default_hacks = [
        Hack('he1display',
            url='https://c-beam.cbrp3.c-base.org/he1display',
            scripts=[]
        ),
        Hack('starfield',
            url='http://www.chiptune.com/starfield/starfield.html',
            scripts=[ UserScripts.remove_tags("iframe") ]
        ),
        Hack('reactive-ball',
            url='http://lab.aerotwist.com/webgl/reactive-ball/',
            scripts=[ UserScripts.remove_ids("msg") ]
        ),
        Hack('hatching-glow',
            url='http://www.ro.me/tech/demos/1/index.html',
            scripts=[ UserScripts.remove_ids("info") ]
        ),
        Hack('shadow-map',
            url='http://alteredqualia.com/three/examples/webgl_shadowmap.html',
            scripts=[ UserScripts.remove_ids("info") ]
        ),
        Hack('birds',
            url='http://mrdoob.github.com/three.js/examples/canvas_geometry_birds.html',
            scripts=[ UserScripts.remove_ids("info"), UserScripts.remove_ids("container") ]
        ),

        Hack('gimme-shiny',     url='http://gimmeshiny.com/?seconds=30'),
        Hack('cell-shader',     url='http://www.ro.me/tech/demos/6/index.html'),
        Hack('kinect',          url='http://mrdoob.com/lab/javascript/webgl/kinect/'),
        Hack('conductor',       url='http://www.mta.me/'),

        Hack('flying-toasters', url='http://bryanbraun.github.io/after-dark-css/all/flying-toasters.html'),
    ]

    def __init__(self, important_hacks=None, hacks=None):
        cycles = []
        if important_hacks is not None:
            cycles.append(itertools.cycle(important_hacks))
        if hacks is not None:
            cycles.append(itertools.cycle(hacks))
        else:
            cycles.append(itertools.cycle(self.default_hacks))
        self.super_cycle = itertools.cycle(cycles)

    def print_list(self):
        for hack in cls.hacks:
            print("%15s\t%s" % (hack.name, hack.url))

    def determine_screensaver(self, name=None):
        current_cycle = next(self.super_cycle)
        return next(current_cycle)

