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
		if self.bright > MAX_BRIGHT:
			self.bright = MAX_BRIGHT
			return False
		if self.bright < 0:
			self.bright = 0
			return False

		colorSum = self.r + self.g + self.b
		if(colorSum > MAX_COLOR):
			ratio = float(colorSum) / MAX_COLOR
			self.r = int(self.r * ratio)
			self.g = int(self.g * ratio)
			self.b = int(self.b * ratio)
			return False

		return True

	def computeGrad(self, curr, next, dt, limit):
		if next == curr:
			return 0

		res = dt / float(next - curr)
		if abs(res) <= 1:
			res = 1 if res > 0 else -1
		elif res > 0:
			res = int(res + 1)
			if res > limit:
				res = limit
		else:
			res = int(res - 1)
			if res < -limit:
				res = -limit

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
		else:
			self.rbright = 1
			self.dbright = self.computeGrad(self.bright, next.bright, dt, 15)

		self.dr = self.computeGrad(self.r, next.r, dt, 15)
		self.dg = self.computeGrad(self.g, next.g, dt, 15)
		self.db = self.computeGrad(self.b, next.b, dt, 15)

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
	def __init__(self, bright, forceBright=False):
		self.type = 'change'
		self.addressList = [63]
		self.color = LightColor(bright, 0, 0, 0, forceBright)

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
		return True

	def update(self, currTime):
		"""Should return a list of updates
		"""
		commands = []
		# First check for brightness optimization
		if self.isConstantBrightness(self.colors) and ((not self.isConstantBrightness(self.prevColors)) or self.colors[0].bright != self.prevColors[0].bright):
			commands.append(GlobalBrightnessChange(self.colors[0].bright))
			for color in self.prevColors:
				color.bright = self.colors[0].bright

		newColors = {}
		for i in xrange(50):
			newColor = self.colors[i]
			prevColor = self.prevColors[i]
			if self.autoGradient:
				nextColor = self.nextColors[i]
				newColor.setGradientTo(nextColor, self.interval)
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

	def runUpdate(self):
		self.interface.sendClear()
		self.interface.drainBytes()
		self.setCurrentTime(0, 0)
		self.sendChangesForTime([ColorChange(list(xrange(50)), LightColor(0xcc, 0, 0, 0, True))], 0) # Turn everything off
		currTime = 0
		while True:
			# if self.prevColors is None:
			# 	self.colorListUpdate(currTime)
			self.prevColors = copy.deepcopy(self.colors)
			if self.autoGradient:
				if self.nextColors is None:
					self.colorListUpdate(currTime)
					self.nextColors = self.colors

				tempColors = copy.deepcopy(self.nextColors)
				self.colors = self.nextColors
				self.colorListUpdate(self.getNextTime(currTime))
				self.nextColors = self.colors
				self.colors = tempColors
			else:
				self.colorListUpdate(currTime)

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
			currTime -= self.period
		return currTime

	def sendChangesForTime(self, changeList, currTime):
		print("Time: %d" % int(currTime * 100))
		return self.interface.sendAtTime(changeList, int(currTime * 100))

	def setCurrentTime(self, currentTime, atTime):
		print("Setting current time to %f", currentTime)
		commands = [TimeMessage(currentTime)]
		print(len(commands))
		return self.interface.sendAtTime(commands, int(atTime * 100))








