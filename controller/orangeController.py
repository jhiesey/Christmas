#!/usr/bin/env python3

import string
import random
from lightlib.abstractLightController import *

class OrangeController(AbstractLightController):
    def __init__(self, port):
        super(OrangeController, self).__init__(port, 60, 0.25, 0, False)
    def colorListUpdate(self, currTime, colors):
        bright = 0xd
        # Make lights flickery
        if random.random() < 0.05:
            bright = 0

        for color in colors:
            color.r = 0xd
            color.g = 0x1
            color.b = 0x0
            color.bright = bright
            color.forceBright = True

controller = OrangeController('/dev/ttyACM0')
controller.runUpdate()
