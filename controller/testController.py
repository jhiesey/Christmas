#!/opt/local/bin/python2.7

from abstractLightController import *

class TestController(AbstractLightController):
	def __init__(self, port):
		super(TestController, self).__init__(port, 1, 6, True)
	def colorListUpdate(self, currTime):
		for (i, color) in enumerate(self.colors):
			color.computeColorGradient = False
			color.r = 0
			color.g = 0
			color.b = 0

			colorTime = (int(currTime / 2) + i) % 3

			if colorTime == 0:
				color.r = 0xc
			elif colorTime == 1:
				color.g = 0xc
			elif colorTime == 2:
				color.b = 0xc

			color.bright = (currTime % 2) * 200

# class TestController(AbstractLightController):
# 	def __init__(self, port):
# 		# super(TestController, self).__init__(port, 0.1, 25)
# 		super(TestController, self).__init__(port, 0.5, 3, True)

# 	# def computeChanges(self, currTime):
# 	# 	commands = []
# 	# 	brightTime = currTime / 2
# 	# 	bright = brightTime * 50
# 	# 	color = LightColor(bright, 0xc, 0xc, 0xc, True)
# 	# 	if currTime % 2 == 0:
# 	# 		commands.append(GlobalBrightnessChange(color))

# 	# 	if currTime % 2 == 1:
# 	# 		redList = []
# 	# 		greenList = []
# 	# 		blueList = []
# 	# 		for i in xrange(50):
# 	# 			index = (brightTime + i) % 3
# 	# 			if index == 0:
# 	# 				redList.append(i)
# 	# 			elif index == 1:
# 	# 				greenList.append(i)
# 	# 			elif index == 2:
# 	# 				blueList.append(i)

# 	# 		commands.append(ColorChange(redList, LightColor(bright, 0xf, 0, 0)))
# 	# 		commands.append(ColorChange(greenList, LightColor(bright, 0, 0xf, 0)))
# 	# 		commands.append(ColorChange(blueList, LightColor(bright, 0, 0, 0xf)))
# 	# 	return commands

# 	# def colorListUpdate(self, currTime):
# 	# 	for color in self.colors:
# 	# 		color.bright = color.bright - 1 if color.bright > 0 else 0

# 	# 	self.colors[int(currTime * 2)].b = 0xc
# 	# 	self.colors[int(currTime * 2)].bright = 0xcc

# 	def colorListUpdate(self, currTime):
# 		for (i, color) in enumerate(self.colors):
# 			color.computeColorGradient = False
# 			color.r = 0
# 			color.g = 0
# 			color.b = 0

# 			colorTime = (int(currTime) + i) % 3

# 			if colorTime == 0:
# 				color.r = 0xc
# 			elif colorTime == 1:
# 				color.g = 0xc
# 			elif colorTime == 2:
# 				color.b = 0xc

# 			color.bright = (currTime % 1) * 400

# 		# global numPasses

# 		# if numPasses > 0 and currTime == 0:
# 		# 	while True:
# 		# 		pass

# 		# numPasses += 1

# 		# self.colors[0].r = 0
# 		# self.colors[0].g = 0
# 		# self.colors[0].b = 0

# 		# if currTime == 0:
# 		# 	self.colors[0].r = 0xc
# 		# elif currTime == 1:
# 		# 	self.colors[0].g = 0xc
# 		# elif currTime == 2:
# 		# 	self.colors[0].b = 0xc

# 		# for i, color in enumerate(self.colors):
# 		# 	color.r = 0
# 		# 	color.g = 0
# 		# 	color.b = 0

# 		# 	index = (currTime + i) % 3

# 		# 	if index == 0:
# 		# 		color.r = 0xc
# 		# 	elif index == 1:
# 		# 		color.g = 0xc
# 		# 	elif index == 2:
# 		# 		color.b = 0xc

controller = TestController('/dev/tty.usbmodemfa141')
controller.runUpdate()