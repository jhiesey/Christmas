#!/opt/local/bin/python2.7

import string
import random
from abstractLightController import *

class TestController(AbstractLightController):
    def __init__(self, port):
        super(TestController, self).__init__(port, 0, 0.1, 0, False)
    def colorListUpdate(self, currTime, colors):
        for color in colors:
            color.r = 0
            color.g = 0
            color.b = 0

            color.bright = 0xcc
        
        changeIndex = random.randrange(50)
        colors[changeIndex].r = 0xd
        colors[changeIndex].g = 0xd
        colors[changeIndex].b = 0xd

class StrobeController(AbstractLightController):
    def __init__(self, port):
        super(StrobeController, self).__init__(port, 0.1, 0.005, 0, False)
    def colorListUpdate(self, currTime, colors):
        for i, color in enumerate(colors):
            if (currTime == 0) == (i < 25):
                color.r = 0
                color.g = 0
                color.b = 0
#            else:
#		color.r = 0xd
#		color.g = 0xd
#		color.b = 0xd
            elif abs(currTime - 0.1) < 0.01:
                color.r = 0xd
            elif abs(currTime - 0.3) < 0.01:
                color.g = 0xd
            elif abs(currTime - 0.5) < 0.01:
                color.b = 0xd
            color.bright = 0xcc

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


class ColorTestController(AbstractLightController):
    def __init__(self, port):
        super(ColorTestController, self).__init__(port, 1, 1, 0, True)
        self.color = LightColor(0xcc, 0xd, 0xd, 0xd)

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

class RainbowController(AbstractLightController):
    def __init__(self, port):
        # super(RainbowController, self).__init__(port, 0.35, 0.05, 0, False)
        super(RainbowController, self).__init__(port, 7, 1, 0.05, False)

    def colorListUpdate(self, currTime, colors):
        for i, color in enumerate(colors):
            # index = (currTime * 20 + i) % 7
            index = (currTime + i) % 7
            #index = currTime % 7
            # index = random.randrange(7)

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
        super(HalfRainbowController, self).__init__(port, 4, 1, 0.05, False)

    def colorListUpdate(self, currTime, colors):
        for i, color in enumerate(colors):
            #index = (currTime * 20 + i) % 7
            index = (currTime + i) % 4

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

class WhiteController(AbstractLightController):
    def __init__(self, port):
        super(WhiteController, self).__init__(port, 60, 30, 0, False)
    def colorListUpdate(self, currTime, colors):
        for color in colors:
            color.r = 0xd
            color.g = 0xd
            color.b = 0xd

class TwinkleController(AbstractLightController):
    def __init__(self,port):
        super(TwinkleController, self).__init__(port, 60, 1, 0.05, False)
        self.offset = [random.uniform(1, 2) for i in xrange(50)]
    def colorListUpdate(self, currTime, colors):
        for (i, color) in enumerate(colors):
            color.r = 0
            color.g = 0
            color.b = 0xd
            # if currTime * self[offset]
            if color.bright == 0:
                if random.uniform(0, self.offset[i]) < 0.5:
                    color.bright = 0xcc
            else:
                color.bright = 0

# class TwinkleController(AbstractLightController):
#     def __init__(self,port):
#         super(TwinkleController, self).__init__(port, 60, 1, 0.05, False)
#         self.speed = random.uniform(1, 5)
#     def colorListUpdate(self, currTime, colors):
#         m = 0
#         for color in colors:
#             color.bright = max(color.bright - (5.0 / 0xcc), 0)
#             m = max(m, color.bright)

#             if m == 0:


            
        

controller = RainbowController('/dev/tty.usbmodemfa2311')
controller.runUpdate()
