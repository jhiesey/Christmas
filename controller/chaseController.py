#!/opt/local/bin/python2.7

import string
import random
from lightlib.abstractLightController import *

class ChaseController(AbstractLightController):
    def __init__(self, port):
        super(ChaseController, self).__init__(port, 0, 0.01, 0, False)
        self.currLight = 0
        self.turnOn = True
    def colorListUpdate(self, currTime, colors):
        bright = 0xd if self.turnOn else 0

        colors[self.currLight].r = bright
        colors[self.currLight].g = bright
        colors[self.currLight].b = bright
        colors[self.currLight].bright = 0xcc

        if self.turnOn:
            self.turnOn = False
        else:
            self.turnOn = True
            self.currLight = (self.currLight + 1) % 50


#         for i, color in enumerate(colors):
#             if (currTime == 0) == (i < 25):
#                 color.r = 0
#                 color.g = 0
#                 color.b = 0
# #            else:
# #       color.r = 0xd
# #       color.g = 0xd
# #       color.b = 0xd
#             elif abs(currTime - 0.1) < 0.01:
#                 color.r = 0xd
#             elif abs(currTime - 0.3) < 0.01:
#                 color.g = 0xd
#             elif abs(currTime - 0.5) < 0.01:
#                 color.b = 0xd
#             color.bright = 0xcc

controller = ChaseController('/dev/tty.usbmodemfa2311')
controller.runUpdate()
