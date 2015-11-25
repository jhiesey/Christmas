from lightlib import interfaceProtocol
from lightlib import lightColor
import time
import copy

class AbstractLightController(object):
	"""To write a new light controller (pattern generator)
	you must create a subclass of this class. The subclass
	must override colorListUpdate() and, optionally,
	waitForRealTime().

	The lights are controlled by creating a controller. In
	the controller, there is a current time measured in seconds
	that increments by self.interval until it reaches or exceeds
	self.period, after which it resets to 0. Although the time
	is represented as a floating point number, in hardware it
	is rounded to the nearest 10ms. The period must also not be
	more than 655 seconds.

	Every time the current time changes, colorListUpdate() is called,
	passing in the current time and a Python list of the colors of the
	lights before the update as lightColor.Color objects. It is the
	job of colorListUpdate() to change the colors to be correct for the
	new time.

	There is also a self.microInterval interval, which must be finer
	than self.interval, and represents a micro timestep used to
	linearly interpolate between values gotten for colorListUpdate().
	This is useful for allowing automatic smooth color transitions.

	Finally, there is a self.syncTime option which causes the waitForRealTime()
	function to get called whenever the current time resets to zero, which
	allows the user to block until some event has happened. It is also
	acceptable for the user to block inside colorListUpdate().

	The self.syncTime option also causes the lights' hardware buffer to be
	cleared when the time is reset to zero. This allows the system to
	work properly even if the internal timer in the lights runs a little
	slower than desired.
	"""

	def __init__(self, port, period, interval=1, microInterval=0, syncTime=False):
		"""Initializes a controller
		port: The serial/usb port to use (e.g. /dev/ttySerial)
		period: The length of time in seconds before time resets to zero (seconds)
		interval: The timestep for updating colors
		microInterval: the micro timestep for color interpolation. Set to zero to
			disable interpolation
		syncTime: Set to True to allow synchronizing with real-time events once per period
		"""
		self.interface = interfaceProtocol.SerialInterface(port)
		self.period = period # Repetition period
		self.interval = interval # Sample interval
		self.microInterval = microInterval # For interpolation
		self.syncTime = syncTime

	def colorListUpdate(self, currTime, colors):
		"""Must be overridden. The colors list should be changed to match the desired
		light colors at currTime
		"""
		pass


	def waitForRealTime(self):
		"""May be overridden. Should block until some real-time event occurs that should
		correspond to the period expring
		"""
		pass

	def isConstantBrightness(self, colorList):
		"""Determines if all lights have the same brightness. If so, this
		allows a significant optimization
		"""
		for i in xrange(1, 50):
			if colorList[i].bright != colorList[i - 1].bright:
				return False

		return True

	def canForceChangeAll(self, curr, next):
		"""Returns True if an immediate brightness change to all lights is valid"""
		changeNeeded = False

		for i in xrange(50):
			if not next[i].forceBright:
				return False
			if curr[i].bright != next[i].bright:
				changeNeeded = True

		return changeNeeded

	def brightInterpolate(self, addr, currBright, next):
		"""Generates a series of brightness change commands
		to get from brightness currBright to next
		"""
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
			commands.append(interfaceProtocol.ColorChangeMessage(addr, outColor))
			firstRun = False

		return commands


	def computeChanges(self, curr, next):
		"""Computes a set of commands needed to change the state from the
		list of colors in curr to the list of colors in next. This is somewhat
		like computing a diff between curr and next, except that certain
		optimizations are also applied
		"""
		commands = []

		# Determine if a global brightness update is valid/useful
		if self.isConstantBrightness(next) and (((curr[0].bright != next[0].bright) and self.isConstantBrightness(curr)) or self.canForceChangeAll(curr, next)):
			commands.extend(self.brightInterpolate(63, curr[0].bright, next[0]))
			for color in curr:
				color.bright = next[0].bright

		for i in xrange(50):
			currColor = curr[i]
			nextColor = next[i]

			if nextColor != currColor:
				commands.extend(self.brightInterpolate(i, currColor.bright, nextColor))

		return commands


	def runColorListUpdate(self, currTime, colors):
		"""Calls colorListUpdate() and normalizes the result"""
		self.colorListUpdate(currTime, colors)
		for color in colors:
			color.normalize()

	def runInterpolation(self, prev, curr, next, microTime):
		"""Computes a set of updates needed to go from prev to
		next given that we are microTime/self.interval of the
		way through the transition. Updates the current values
		(mid-interpolation) in curr and returns the needed updates.
		"""
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
		"""Initializes the lights by resetting the input buffer ans setting
		all lights to full brightness with r, g, and b set to 0.
		"""
		self.interface.sendClear(False)
		self.interface.drainBytes()
		self.clearTime(0)
		self.sendChangesForTime([interfaceProtocol.ColorChangeMessage(i, lightColor.Color(0xcc, 0, 0, 0, True)) for i in xrange(50)], 0) # Turn everything off
		time.sleep(1) # Make sure everything is set


	def mainLoop(self):
		"""The main loop that computes the correct values and updates the lights"""
		currColors = [lightColor.Color(0xcc, 0, 0, 0) for i in xrange(50)]
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
					self.interface.sendClear()
				self.clearTime(resetTime)
				resetTime = None

			if self.microInterval != 0:
				microTemp = copy.deepcopy(currColors)
				microTime = 0
				while microTime < self.interval:
					updates = self.runInterpolation(currColors, microTemp, nextColors, microTime)
					self.sendChangesForTime(updates, currTime + microTime)

					microTime += self.microInterval
				updates = self.computeChanges(microTemp, nextColors) # Make sure everything is up to date (even if no gradient)
				self.sendChangesForTime(updates, currTime + self.interval)
				currColors = microTemp

			else:
				updates = self.computeChanges(currColors, nextColors)
				self.sendChangesForTime(updates, currTime)

			currColors = nextColors
			newTime = self.getNextTime(currTime)
			if newTime == 0:
				resetTime = currTime + self.interval

			currTime = newTime		

	def runUpdate(self):
		"""The main entry point. This might need to be changed in the future to provide an easy way to change
		between different patterns without resetting everything
		"""
		try:
			self.initLights()
			self.mainLoop()
		except interfaceProtocol.LightError as e:
			print(e)


	def getNextTime(self, currTime):
		"""Computes the next timestep after currTime"""
		currTime += self.interval
		if currTime >= self.period:
			currTime = 0
		return currTime

	def sendChangesForTime(self, changeList, currTime):
		"""Sends all updates out of a list"""
		for change in changeList:
			self.interface.sendMessage(change, int(currTime * 100))

	def clearTime(self, currTime):
		"""Clears the hardware time"""
		self.interface.sendMessage(interfaceProtocol.TimeMessage(), int(currTime * 100))
