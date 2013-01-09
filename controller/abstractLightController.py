import interfaceProtocol
import time

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
	def __init__(self, port, interval=0.01, period=60):
		self.interface = interfaceProtocol.SerialInterface(port)
		self.interval = interval # Sample interval
		self.period = period # Repetition period
		self.notifiedTime = -1

	def update(self, currTime):
		"""Should return a list of colors
		"""
		print("Error: update not implemented!")
		exit(1)

	def runUpdate(self):
		self.interface.drainBytes() # Still technically a race condition here
		self.interface.sendClear()
		self.setCurrentTime(0, 0)
		currTime = 0
		while True:
			changeList = self.update(currTime)
			status = self.sendChangesForTime(changeList, currTime)
			if status < 0:
				print("Failure!")
				return

			print(("currTime: %d", currTime))
			currTime += self.interval
			print(("currTime: %d", currTime))
			while currTime >= self.period:
				prevTime = currTime
				currTime -= self.period
				status = self.setCurrentTime(currTime, prevTime)
				if status < 0:
					print("Failure!")
					return


	def sendChangesForTime(self, changeList, currTime):
		print("Time: %d" % int(currTime * 100))
		return self.interface.sendAtTime(changeList, int(currTime * 100))

	def setCurrentTime(self, currentTime, atTime):
		print("Setting current time to %f", currentTime)
		commands = [TimeMessage(currentTime)]
		print(len(commands))
		return self.interface.sendAtTime(commands, int(atTime * 100))








