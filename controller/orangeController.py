#!/usr/bin/env python3

import string
import random
from lightlib.abstractLightController import *

class OrangeController(AbstractLightController):
    def __init__(self, port):
        super(OrangeController, self).__init__(port, 60, 30, 0, False)
    def colorListUpdate(self, currTime, colors):
        for color in colors:
            color.r = 0xd
            color.g = 0x1
            color.b = 0x0

controller = OrangeController('/dev/ttyACM0')
controller.runUpdate()
