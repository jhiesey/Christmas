#!/opt/local/bin/python2.7

import string
import random
from lightlib.abstractLightController import *

class StrobeController(AbstractLightController):
    def __init__(self, port):
        super(StrobeController, self).__init__(port, 0.1, 0.005, 0, False)
    def colorListUpdate(self, currTime, colors):
        for i, color in enumerate(colors):
            if currTime == 0:
                color.r = 0
                color.g = 0
                color.b = 0
            else:
                color.r = 0xd
                color.g = 0xd
                color.b = 0xd

controller = StrobeController('/dev/tty.usbmodemfd1311')
controller.runUpdate()
