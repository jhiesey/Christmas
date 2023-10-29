#!/usr/bin/env python3

import string
import random
from lightlib.abstractLightController import *

BRIGHT_DECREASE = 5

class VolcanoController(AbstractLightController):
    def __init__(self, port):
        super(VolcanoController, self).__init__(port, 7, 0.01, 0, False)

    def colorListUpdate(self, currTime, colors):
        for i, color in enumerate(colors):
            if random.random() < 0.03:
            	color.bright = 0xcc
            	color.r = 15
            	color.g = random.randrange(0, 8)
            	color.b = 0
            elif color.bright >= BRIGHT_DECREASE:
            	color.bright -= BRIGHT_DECREASE
            else:
                color.bright = 0

            color.forceBright = True

controller = VolcanoController('/dev/ttyACM0')
controller.runUpdate()

