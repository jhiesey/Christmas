import interfaceProtocol
import time
import copy

MAX_BRIGHT = 0xcc
MAX_COLOR = 0xc * 3

class LightColor(object):
	def __init__(self, bright, r, g, b, forceBright=False):
		self.bright = bright
		self.forceBright = forceBright
		self.r = r
		self.g = g
		self.b = b
		self.normalize()
		self.hasGradient = False

	def normalize(self):
		valid = True

		if self.bright > MAX_BRIGHT:
			self.bright = MAX_BRIGHT
			valid = False
		if self.bright < 0:
			self.bright = 0
			valid = False

		colorSum = self.r + self.g + self.b
		if(colorSum > MAX_COLOR):
			ratio = MAX_COLOR / float(colorSum)
			self.r = int(self.r * ratio)
			self.g = int(self.g * ratio)
			self.b = int(self.b * ratio)
			valid = False

		return valid

	def computeGrad(self, curr, next, dt, limit):
		if next == curr:
			return 0

		res = dt / float(next - curr)
		if abs(res) <= 1:
			res = 1 if res > 0 else -1
		elif abs(res) > limit:
			res = 0
		elif res > 0:
			res = int(res + 0.9)
		else:
			res = int(res - 0.9)

		return res


	def setGradientTo(self, next, dt):
		if self.colorEqual(next):
			self.hasGradient = False
			return

		dt = dt * 100

		brightDiff = next.bright - self.bright
		rate = float(brightDiff) / dt
		if rate == 0:
			self.rbright = 0
			self.dbright = 0
		elif abs(rate) > 1:
			if rate > 15:
				self.rbright = 15
			elif rate < -15:
				self.rbright = -15
			else:
				self.rbright = int(rate)
			self.dbright = 1
		else:
			self.rbright = 1
			self.dbright = self.computeGrad(self.bright, next.bright, dt, 15)

		self.dr = self.computeGrad(self.r, next.r, dt, 127)
		self.dg = self.computeGrad(self.g, next.g, dt, 127)
		self.db = self.computeGrad(self.b, next.b, dt, 127)

		self.hasGradient = True

	def colorEqual(self, other):
		"""Compares only color, not gradient"""
		if self.bright != other.bright:
			return False
		if self.r != other.r:
			return False
		if self.g != other.g:
			return False
		if self.b != other.b:
			return False
		return True

	def brightEqual(self, other):
		"""Compares only brightness, but INCLUDES gradient"""
		if self.bright != other.bright:
			return False
		if self.hasGradient != other.hasGradient:
			return False
		if self.hasGradient:
			if self.dbright != other.dbright:
				return False
			if self.rbright != other.rbright:
				return False

		return True

	def __ne__(self, other):
		return not self.__eq__(other)

	def __eq__(self, other):
		if not self.colorEqual(other):
			return False
		if self.hasGradient != other.hasGradient:
			return False
		if self.hasGradient:
			if self.dbright != other.dbright:
				return False
			if self.rbright != other.rbright:
				return False
			if self.dr != other.dr:
				return False
			if self.dg != other.dg:
				return False
			if self.db != other.db:
				return False

		return True


	def __hash__(self):
		return hash(self.bright) ^ hash(self.r) ^ hash(self.g) ^ hash(self.b)

class ColorChange(object):
	def __init__(self, addressList, color):
		self.type = 'change'
		self.addressList = addressList
		self.color = color

class GlobalBrightnessChange(object):
	def __init__(self, color):
		self.type = 'change'
		self.addressList = [63]
		self.color = copy.deepcopy(color)
		self.color.r = 0
		self.color.g = 0
		self.color.b = 0
		self.color.dr = 0
		self.color.dg = 0
		self.color.db = 0

class NotificationMessage(object):
	def __init__(self, notificationTime):
		self.type = 'notify'

class TimeMessage(object):
	def __init__(self, currentTime):
		self.type = 'settime'
		self.time = int(currentTime * 100)

class AbstractLightController(object):
	def __init__(self, port, interval, period, autoGradient=False):
		self.interface = interfaceProtocol.SerialInterface(port)
		self.interval = interval # Sample interval
		self.period = period # Repetition period
		self.autoGradient = autoGradient
		self.colors = [LightColor(0xcc, 0, 0, 0) for i in xrange(50)]
		self.prevColors = None
		self.nextColors = None

	def isConstantBrightness(self, colorList):
		for i in xrange(1, 50):
			if colorList[i].bright != colorList[i - 1].bright:
				return False

			if colorList[i].hasGradient != colorList[i - 1].hasGradient:
				return False
			if colorList[i].hasGradient:
				if colorList[i].dbright != colorList[i - 1].dbright:
					return False
				if colorList[i].rbright != colorList[i - 1].rbright:
					return False
		return True

	def update(self, currTime):
		"""Should return a list of updates
		"""
		commands = []
		if self.autoGradient:
			for i in xrange(50): # Compute gradients
				newColor = self.colors[i]
				nextColor = self.nextColors[i]
				newColor.setGradientTo(nextColor, self.interval)

		# First check for brightness optimization
		ignoreBrightnessGradient = False
		if self.isConstantBrightness(self.colors) and not (self.isConstantBrightness(self.prevColors) and self.colors[0].brightEqual(self.prevColors[0])):
			commands.append(GlobalBrightnessChange(self.colors[0]))
			for color in self.prevColors:
				color.bright = self.colors[0].bright
			ignoreBrightnessGradient = True
				# if self.autoGradient:
				# 	color.hasGradient = self.colors[0].hasGradient
				# 	if color.hasGradient:
				# 		color.dbright = self.colors[0].dbright
				# 		color.rbright = self.colors[0].rbright

		newColors = {}
		for i in xrange(50):
			newColor = self.colors[i]
			prevColor = self.prevColors[i]
			# if self.autoGradient:
			# 	nextColor = self.nextColors[i]
			# 	newColor.setGradientTo(nextColor, self.interval)

			if self.autoGradient and ignoreBrightnessGradient:
				newColor.dbright = 0
				newColor.rbright = 0
				prevColor.dbright = 0
				prevColor.rbright = 0

			if newColor != prevColor:
				if newColor in newColors:
					newColors[newColor].append(i)
				else:
					newColors[newColor] = [i]

		for newColor, lights in newColors.items():
			commands.append(ColorChange(lights, newColor))
		return commands

	def colorListUpdate(self, currTime):
		pass

	def runColorListUpdate(self, currTime):
		self.colorListUpdate(currTime)
		for color in self.colors:
			color.normalize()

	def runUpdate(self):
		self.interface.sendClear()
		self.interface.drainBytes()
		self.sendChangesForTime([ColorChange(list(xrange(50)), LightColor(0xcc, 0, 0, 0, True))], 0) # Turn everything off
		time.sleep(1)
		self.setCurrentTime(0, 0)
		currTime = 0
		while True:
			self.prevColors = copy.deepcopy(self.colors)
			if self.autoGradient:
				if self.nextColors is None:
					self.runColorListUpdate(currTime)
					self.nextColors = self.colors

				tempColors = copy.deepcopy(self.nextColors)
				self.colors = self.nextColors
				self.runColorListUpdate(self.getNextTime(currTime))
				self.nextColors = self.colors
				self.colors = tempColors
			else:
				self.runColorListUpdate(currTime)

			changeList = self.update(currTime)
			if len(changeList) > 0:
				status = self.sendChangesForTime(changeList, currTime)
				if status < 0:
					print("Failure!")
					return status

			print(("currTime: %d", currTime))
			currTime += self.interval
			print(("currTime: %d", currTime))
			if currTime >= self.period:
				status = self.setCurrentTime(0, currTime)
				currTime = 0
				if status < 0:
					print("Failure!")
					return status

	def getNextTime(self, currTime):
		currTime += self.interval
		if currTime >= self.period:
			currTime = 0
		print("Next time: %d" % currTime)
		return currTime

	def sendChangesForTime(self, changeList, currTime):
		print("Time: %d" % int(currTime * 100))
		return self.interface.sendAtTime(changeList, int(currTime * 100))

	def setCurrentTime(self, currentTime, atTime):
		print("Setting current time to %f", currentTime)
		commands = [TimeMessage(currentTime)]
		print(len(commands))
		return self.interface.sendAtTime(commands, int(atTime * 100))








