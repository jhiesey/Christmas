#!/opt/local/bin/python2.7

from abstractLightController import *

class TestController(AbstractLightController):
	def __init__(self, port):
		super(TestController, self).__init__(port, 1, 3)

	def update(self, currTime):
		commands = []
		for i in xrange(50):
			index = (currTime + i) % 3
			r = 0
			g = 0
			b = 0
			if index == 0:
				r = 0xf
			elif index == 1:
				g = 0xf
			elif index == 2:
				b = 0xf
			color = LightColor(0xcc, r, g, b)
			commands.append(LightChange([i], color))
		return commands


controller = TestController('/dev/tty.usbmodemfa141')
controller.runUpdate()