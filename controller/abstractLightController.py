import interfaceProtocol
import time
import copy

MAX_BRIGHT = 0xcc
MAX_COLOR = 0xd * 3

class LightColor(object):
	def __init__(self, bright, r, g, b, forceBright=False):
		self.bright = bright
		self.forceBright = forceBright
		self.r = r
		self.g = g
		self.b = b
		self.normalize()
		self.computeColorGradient = True
		self.computeBrightGradient = True

	def normalize(self):
		valid = True
		self.bright = int(self.bright)
		self.r = int(self.r)
		self.g = int(self.g)
		self.b = int(self.b)

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
		return self.colorEqual(other)

class ColorChange(object):
	def __init__(self, address, color):
		self.type = 'change'
		self.address = address
		self.color = color

class TimeMessage(object):
	def __init__(self):
		self.type = 'cleartime'

class AbstractLightController(object):
	def __init__(self, port, period, interval=1, microInterval=0, syncTime=False):
		self.interface = interfaceProtocol.SerialInterface(port)
		self.period = period # Repetition period
		self.interval = interval # Sample interval
		self.microInterval = microInterval # For interpolation
		self.syncTime = syncTime

	def isConstantBrightness(self, colorList):
		for i in xrange(1, 50):
			if colorList[i].bright != colorList[i - 1].bright:
				return False

		return True

	def brightInterpolate(self, addr, currBright, next):
		commands = []
		firstRun = True
		while currBright != next.bright or firstRun:
			if next.forceBright or currBright == next.bright:
				currBright = next.bright
			elif currBright < next.bright:
				currBright += 1
			else:
				currBright -= 1

			outColor = copy.deepcopy(next);
			outColor.bright = currBright
			commands.append(ColorChange(addr, outColor))
			firstRun = False

		return commands


	def computeChanges(self, curr, next):
		"""Returns a list of updates"""
		commands = []

		if self.isConstantBrightness(next) and (curr[0].bright != next[0].bright or not self.isConstantBrightness(curr)):
			commands.extend(self.brightInterpolate(63, curr[0].bright, next[0])) #commands.append(ColorChange(63, next[0]))
			for color in curr:
				color.bright = next[0].bright

		for i in xrange(50):
			currColor = curr[i]
			nextColor = next[i]

			if nextColor != currColor:
				commands.extend(self.brightInterpolate(i, currColor.bright, nextColor))

		return commands

	def colorListUpdate(self, currTime):
		pass

	def runColorListUpdate(self, currTime, colors):
		self.colorListUpdate(currTime, colors)
		for color in colors:
			color.normalize()

	def runInterpolation(self, prev, curr, next, microTime):
		frac = float(microTime) / self.interval
		newCurr = []
		for i in xrange(50):
			c = copy.deepcopy(curr[i])
			if curr[i].computeBrightGradient:
				c.bright = int(prev[i].bright * (1 - frac) + next[i].bright * frac + 0.5)

			if curr[i].computeColorGradient:
				c.r = int(prev[i].r * (1 - frac) + next[i].r * frac + 0.5)
				c.g = int(prev[i].g * (1 - frac) + next[i].g * frac + 0.5)
				c.b = int(prev[i].b * (1 - frac) + next[i].b * frac + 0.5)

			newCurr.append(c)

		updates = self.computeChanges(curr, newCurr)
		curr[:] = newCurr
		return updates


	def initLights(self):
		self.interface.sendClear(False)
		self.interface.drainBytes()
		self.clearTime(0)
		self.sendChangesForTime([ColorChange(i, LightColor(0xcc, 0, 0, 0, True)) for i in xrange(50)], 0) # Turn everything off
		time.sleep(1) # Make sure everything is set

	def waitForRealTime(self):
		pass

	def runUpdate(self):
		self.initLights()
		currColors = [LightColor(0xcc, 0, 0, 0) for i in xrange(50)]
		currTime = 0
		resetTime = 0
		while True:
			if self.syncTime and (resetTime is not None):
				self.waitForRealTime() # Allows blocking

			nextColors = copy.deepcopy(currColors)
			if self.microInterval == 0:
				self.runColorListUpdate(currTime, nextColors)
			else:
				self.runColorListUpdate(self.getNextTime(currTime), nextColors)

			if resetTime is not None:
				if self.syncTime:
					status = self.interface.sendClear()
					if status == 0:
						status = self.clearTime(0)
					if status < 0:
						print("Failure!")
						return status
				else:
					status = self.clearTime(resetTime)
					if status < 0:
						print("Failure!")
						return status
				resetTime = None

			if self.microInterval != 0:
				microTemp = copy.deepcopy(currColors)
				microTime = 0
				while microTime < self.interval:
					updates = self.runInterpolation(currColors, microTemp, nextColors, microTime)
					status = self.sendChangesForTime(updates, currTime + microTime)
					if status < 0:
						print("Failure!")
						return status

					microTime += self.microInterval
				updates = self.computeChanges(microTemp, nextColors) # Make sure everything is up to date (even if no gradient)
				status = self.sendChangesForTime(updates, currTime + self.interval)
				if status < 0:
					print("Failure!")
					return status
				currColors = microTemp

			else:
				updates = self.computeChanges(currColors, nextColors)
				status = self.sendChangesForTime(updates, currTime)
				if status < 0:
					print("Failure!")
					return status

			currColors = nextColors
			newTime = self.getNextTime(currTime)
			if newTime == 0:
				resetTime = currTime + self.interval

			currTime = newTime

	def getNextTime(self, currTime):
		currTime += self.interval
		if currTime >= self.period:
			currTime = 0
		return currTime

	def sendChangesForTime(self, changeList, currTime):
		for change in changeList:
			status = self.interface.sendMessage(change, int(currTime * 100))
			if status != 0:
				return status
		return 0

	def clearTime(self, currTime):
		return self.interface.sendMessage(TimeMessage(), int(currTime * 100))
