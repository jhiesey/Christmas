#!/usr/bin/env python3

import time
from lightlib.abstractLightController import *

class FallController(AbstractLightController):
    def __init__(self, port):
        super(FallController, self).__init__(port, 0, 0, 0, False)
        self._bright = 0
    def colorListUpdate(self, currTime, colors):
        time.sleep(1)
        try:
            with open('brightness.txt', 'r') as f:
                self._bright = min(max(float(f.readline()), 0), 1)
        except Exception as e:
            print("Could not read brightness configuration: %s" % (e,))

        for i, color in enumerate(colors):
            c = i % 3
            if c == 0:
                color.r = 13
                color.g = 0
                color.b = 0
                color.bright = 204 * self._bright
            elif c == 1:
                color.r = 13
                color.g = 7
                color.b = 0
                color.bright = 150 * self._bright
            elif c == 2:
                color.r = 11
                color.g = 1
                color.b = 0
                color.bright = 50 * self._bright

controller = FallController('/dev/ttyACM0')
controller.runUpdate()

