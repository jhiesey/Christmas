#!/usr/bin/env python3

import time
from lightlib.abstractLightController import *

PERIOD = 50
TICK_TIME = 0.25
TICKS_PER_PERIOD = PERIOD/TICK_TIME

class ChristmaHanukkahController(AbstractLightController):
    def __init__(self, port):
        super(ChristmaHanukkahController,  self).__init__(port, 60, 0.25, 0, False)
        self._bright = 0
    def colorListUpdate(self, currTime, colors):
        # time.sleep(1)
        try:
            with open('brightness.txt', 'r') as f:
                self._bright = min(max(float(f.readline()), 0), 1)
        except Exception as e:
            print("Could not read brightness configuration: %s" % (e,))

        tickCount = currTime/TICK_TIME

        for i, color in enumerate(colors):
            color.bright = 204 * self._bright
            print(i, tickCount + i)

            c = i % 2
            if (tickCount + i) % TICKS_PER_PERIOD >= TICKS_PER_PERIOD / 2:
                if c == 0:
                    color.r = 13
                    color.g = 13
                    color.b = 13
                else:
                    color.r = 0
                    color.g = 0
                    color.b = 13
            else:
                if c == 0:
                    color.r = 13
                    color.g = 0
                    color.b = 0
                elif c == 1:
                    color.r = 0
                    color.g = 13
                    color.b = 0

controller = ChristmaHanukkahController('/dev/ttyACM0')
controller.runUpdate()
