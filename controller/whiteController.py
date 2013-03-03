#!/opt/local/bin/python2.7

import string
import random
from abstractLightController import *

class WhiteController(AbstractLightController):
    def __init__(self, port):
        super(WhiteController, self).__init__(port, 60, 30, 0, False)
    def colorListUpdate(self, currTime, colors):
        for color in colors:
            color.r = 0xd
            color.g = 0xd
            color.b = 0xd

controller = WhiteController('/dev/tty.usbmodemfd1311')
controller.runUpdate()
