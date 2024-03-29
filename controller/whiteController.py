#!/usr/bin/env python3

import string
import random
from lightlib.abstractLightController import *

class WhiteController(AbstractLightController):
    def __init__(self, port):
        super(WhiteController, self).__init__(port, 60, 30, 0, False)
    def colorListUpdate(self, currTime, colors):
        for color in colors:
            color.r = 0xd
            color.g = 0xd
            color.b = 0xd

controller = WhiteController('/dev/ttyACM0')
controller.runUpdate()
