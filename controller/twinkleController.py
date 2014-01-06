#!/opt/local/bin/python2.7

import string
import random
from lightlib.abstractLightController import *

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


            
        

controller = TwinkleController('/dev/tty.usbmodem14511')
controller.runUpdate()
