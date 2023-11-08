#!/usr/bin/env python3

import string
import random
from lightlib.abstractLightController import *

class FallController(AbstractLightController):
    def __init__(self, port):
        super(FallController, self).__init__(port, 60, 30, 0, False)
    def colorListUpdate(self, currTime, colors):
        for i, color in enumerate(colors):
            c = i % 3
            if c == 0:
                color.r = 13
                color.g = 0
                color.b = 0
                color.bright = 204
            elif c == 1:
                color.r = 13
                color.g = 7
                color.b = 0
                color.bright = 204
            elif c == 2:
                color.r = 11
                color.g = 1
                color.b = 0
                color.bright = 50

controller = FallController('/dev/ttyACM0')
controller.runUpdate()
