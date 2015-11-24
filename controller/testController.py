#!/usr/bin/env python

import string
import random
from lightlib.abstractLightController import *
import lightlib.lightColor

class TestController(AbstractLightController):
    def __init__(self, port):
        super(TestController, self).__init__(port, 0, 0.5, 0, False)
    def colorListUpdate(self, currTime, colors):
        for color in colors:
            color.r = 0xd
            color.g = 0xd
            color.b = 0xd

            color.bright = random.randrange(0xcd)
            color.forceBright = True

class ColorTestController(AbstractLightController):
    def __init__(self, port):
        super(ColorTestController, self).__init__(port, 1, 1, 0, True)
        self.color = lightColor.Color(0xcc, 0xd, 0xd, 0xd)

    def waitForRealTime(self):
        while True:
            inp = raw_input("Enter c v: ")
            try:
                args = string.split(inp)

                color = args[0]
                value = int(args[1])

                print(color)
                print(value)

                if color == 'r':
                    self.color.r = value
                    break
                elif color == 'g':
                    self.color.g = value
                    break
                elif color == 'b':
                    self.color.b = value
                    break
            except:
                pass
            print("Invalid input!")



    def colorListUpdate(self, currTime, colors):
        for i in xrange(50):
            colors[i] = copy.deepcopy(self.color)


controller = TestController('/dev/tty.usbmodem1411')
controller.runUpdate()
