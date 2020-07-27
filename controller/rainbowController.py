#!/usr/bin/env python3

import string
import random
from lightlib.abstractLightController import *

class RainbowController(AbstractLightController):
    def __init__(self, port):
        # super(RainbowController, self).__init__(port, 0.35, 0.05, 0, False)
        super(RainbowController, self).__init__(port, 7, 0.25, 0.05, False)
        self._bright = 1

    def colorListUpdate(self, currTime, colors):

        if currTime % 1 == 0:
            try:
                with open('brightness.txt', 'r') as f:
                    self._bright = min(max(float(f.readline()), 0), 1)
            except Exception as e:
                print("Could not read brightness configuration: %s" % (e,))

        scaledBright = self._bright * 0xcc

        for i, color in enumerate(colors):
            # index = (currTime * 20 + i) % 7
            index = (currTime * 4 + i) % 7
            #index = currTime % 7
            # index = random.randrange(7)
            color.bright = scaledBright

            if index == 0:
                color.r = 13
                color.g = 0
                color.b = 0
            elif index == 1:
                color.r = 11
                color.g = 1
                color.b = 0
            elif index == 2:
                color.r = 13
                color.g = 7
                color.b = 0
            elif index == 3:
                color.r = 1
                color.g = 13
                color.b = 0
            elif index == 4:
                color.r = 0
                color.g = 1
                color.b = 13
            elif index == 5:
                color.r = 2
                color.g = 0
                color.b = 13
            elif index == 6:
                color.r = 8
                color.g = 0
                color.b = 13


class HalfRainbowController(AbstractLightController):
    def __init__(self, port):
        #super(RainbowController, self).__init__(port, 0.35, 0.05, 0, False)
        super(HalfRainbowController, self).__init__(port, 4, 0.25, 0.05, False)

    def colorListUpdate(self, currTime, colors):
        for i, color in enumerate(colors):
            #index = (currTime * 20 + i) % 7
            index = (currTime * 4 + i) % 4

            if index == 0:
                color.r = 1
                color.g = 13
                color.b = 0
            elif index == 1:
                color.r = 0
                color.g = 1
                color.b = 13
            elif index == 2:
                color.r = 2
                color.g = 0
                color.b = 13
            elif index == 3:
                color.r = 8
                color.g = 0
                color.b = 13

controller = RainbowController('/dev/ttyACM0')
controller.runUpdate()
