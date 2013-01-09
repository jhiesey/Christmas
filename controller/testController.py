#!/opt/local/bin/python2.7

from abstractLightController import *

class TestController(AbstractLightController):
	def __init__(self, port):
		super(TestController, self).__init__(port, 1, 6)

	def update(self, currTime):
		commands = []
		brightTime = currTime / 2
		bright = brightTime * 50
		color = LightColor(bright, 0xc, 0xc, 0xc, True)
		if currTime % 2 == 0:
			commands.append(GlobalBrightnessChange(bright, True))

		if currTime % 2 == 1:
			redList = []
			greenList = []
			blueList = []
			for i in xrange(50):
				index = (brightTime + i) % 3
				if index == 0:
					redList.append(i)
				elif index == 1:
					greenList.append(i)
				elif index == 2:
					blueList.append(i)

				if len(redList) > 4:
					commands.append(ColorChange(redList, LightColor(bright, 0xf, 0, 0)))
					redList = []
					
			commands.append(ColorChange(greenList, LightColor(bright, 0, 0xf, 0)))
			commands.append(ColorChange(blueList, LightColor(bright, 0, 0, 0xf)))


				# r = 0
				# g = 0
				# b = 0
				# if index == 0:
				# 	r = 0xf
				# elif index == 1:
				# 	g = 0xf
				# elif index == 2:
				# 	b = 0xf
				# color = LightColor(bright, r, g, b)
				# commands.append(ColorChange([i], color))
		return commands


controller = TestController('/dev/tty.usbmodemfa141')
controller.runUpdate()