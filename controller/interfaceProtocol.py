import interfaceIO
import struct

class SerialInterface(object):

	def __init__(self, port):
		self.connection = interfaceIO.InterfaceIO(port, 1000)
		self.lastTime = -1

	def changeLights(self, lights, setting):
		numLights = len(lights)
		if numLights == 1:
			self.changeSingle(lights[0], setting)
		elif numLights < 8:
			self.changeList(lights, setting)
		else:
			mask = [0 for i in xrange(7)]
			for light in lights:
				if light == 64:
					mask[7] |= 8
				else:
					mask[light / 8] |= 1 << (light % 8)
			self.changeMask(mask, setting)

	def changeSingle(self, light, setting):
		cmdByte = 0x10
		if setting.forceBright:
			cmdBright |= 0x4
		self.connection.sendBytes(struct.pack('!BB', cmdByte, light))
		self.sendSetting(setting)

	def changeList(self, lights, setting):
		cmdByte = 0x20
		if setting.forceBright:
			cmdBright |= 0x4
		self.connection.sendBytes(struct.pack('!BB', cmdByte, len(lights)))
		for light in lights:
			self.conneciton.sendBytes(struct.pack('!B', light))
		self.sendSetting(setting)

	def changeMask(self, mask, setting):
		cmdByte = 0x30
		if setting.forceBright:
			cmdBright |= 0x4
		self.connection.sendBytes(struct.pack('!BB', cmdByte, 7))
		for i in xrange(7):
			self.connection.sendBytes(struct.pack('!B', mask[i]))
		self.sendSetting(setting)

	def sendSetting(self, setting):
		colorVal = (setting.b << 8) | (setting.g << 4) | setting.r
		self.connection.sendBytes(struct.pack('!BH', setting.bright, colorVal))

	def getStatus(self):
		response = self.connection.receiveBytes(1)
		while True:
			if len(response) == 0:
				print("Too short")
				return -1

			code = struct.unpack('!B', response[0])[0]
			if code == 0:
				return 0
			if code == 0x80:
				return 1
			if code == 0x1:
				print("Got time")
				timeValue = self.connection.receiveBytes(2)
				if len(timeValue) != 2:
					return -1
				self.lastTime = struct.unpack('!H', timeValue)[0]

			else:
				return -1

	def sendAtTime(self, commandList, time, resetAtEnd=False):
		cmdByte = 0x20
		if resetAtEnd:
			cmdByte |= 0x10
		self.connection.sendBytes(struct.pack('!BH', cmdByte, time))
		for command in commandList:
			if command.type == 'change':
				self.changeLights(command.addressList, command.color)
			elif command.type == 'notify':
				self.connection.sendBytes(struct.pack('!BH', 0x80, command.time))
			elif command.type == 'settime':
				self.connection.sendBytes(struct.pack('!BH', 0x90, command.time))

		self.connection.sendBytes(struct.pack('!B', 0))
		status = self.getStatus()
		print(status)
		return status

	def sendClear(self):
		self.connection.sendBytes(struct.pack('!B', 0))
		return self.getStatus()

	def waitForTime(self, waitTime):
		intTime = int(waitTime * 100)
		if intTime == self.lastTime:
			return True

		message = ""
		while True:
			message += self.connection.receiveBytes(3 - len(message))
			if len(message) != 3:
				continue

			decodedMsg = struct.unpack('!BH', message)
			message = []
			if decodedMsg[0] == 0x1:
				if decodedMsg[1] == intTime:
					return True
			else:
				print(decodedMsg[0])
				assert(False)
				return False



