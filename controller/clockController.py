#!/opt/local/bin/python2.7

import string
import random
from abstractLightController import *

class ClockController(AbstractLightController):
    def __init__(self, port):
        super(ClockController, self).__init__(port, 60, 1, 0, True)

    def waitForRealTime(self):
        time.sleep(2)
        timeDiff = 1
        timeSecs = time.time()
        realTime = time.localtime(timeSecs)
        sleepTime = 60 - (realTime.tm_sec + timeSecs % 1)
        if sleepTime < 0:
            sleepTime += 60
        print("Sleep time: %f" % sleepTime)
        time.sleep(sleepTime)
        self.realTime = time.localtime(time.time() + 30) # Get the middle of the minute

    def colorListUpdate(self, currTime, colors):
        # Convert to binary
        colors.reverse()
        oddTime = currTime % 2 > 0
        self.writeBinaryAtLight(colors, currTime, 0, 6)
        colors[6].b = 0x3 if oddTime else 0x1
        self.writeBinaryAtLight(colors, self.realTime.tm_min, 7, 6)
        colors[13].b = 0x3 if oddTime else 0x1
        self.writeBinaryAtLight(colors, self.realTime.tm_hour, 14, 5)
        colors.reverse()

    def writeBinaryAtLight(self, colors, val, startLight, numLights):
        for i in xrange(numLights):
            on = val % 2 == 1
            val >>= 1
            colors[i + startLight].r = 0xf if on else 0

controller = ClockController('/dev/tty.usbmodemfd1311')
controller.runUpdate()
