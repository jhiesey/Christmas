import interfaceIO
import struct

class SerialInterface(object):

	def __init__(self, port):
		self.connection = interfaceIO.InterfaceIO(port, 3)
	# 	self.lastTime = -1

	# def changeLights(self, lights, setting):
	# 	numLights = len(lights)
	# 	if numLights == 1:
	# 		self.changeSingle(lights[0], setting)
	# 	elif numLights < 8:
	# 		self.changeList(lights, setting)
	# 	else:
	# 		mask = [0 for i in xrange(7)]
	# 		for light in lights:
	# 			if light >= 50:
	# 				continue
	# 			else:
	# 				mask[light / 8] |= 1 << (light % 8)
	# 		self.changeMask(mask, setting)

	# def changeSingle(self, light, setting):
	# 	cmdByte = 0x10
	# 	if setting.forceBright:
	# 		cmdByte |= 0x4
	# 	if setting.hasGradient:
	# 		cmdByte |= 0x8
	# 	self.connection.sendBytes(struct.pack('!BB', cmdByte, light))
	# 	self.sendSetting(setting)

	# def changeList(self, lights, setting):
	# 	cmdByte = 0x20
	# 	if setting.forceBright:
	# 		cmdByte |= 0x4
	# 	if setting.hasGradient:
	# 		cmdByte |= 0x8
	# 	self.connection.sendBytes(struct.pack('!BB', cmdByte, len(lights)))
	# 	for light in lights:
	# 		self.connection.sendBytes(struct.pack('!B', light))
	# 	self.sendSetting(setting)

	# def changeMask(self, mask, setting):
	# 	cmdByte = 0x30
	# 	if setting.forceBright:
	# 		cmdByte |= 0x4
	# 	if setting.hasGradient:
	# 		cmdByte |= 0x8
	# 	self.connection.sendBytes(struct.pack('!B', cmdByte))
	# 	for i in xrange(7):
	# 		self.connection.sendBytes(struct.pack('!B', mask[i]))
	# 	self.sendSetting(setting)

	# def sendSetting(self, setting):
	# 	colorVal = (setting.b << 8) | (setting.g << 4) | setting.r
	# 	self.connection.sendBytes(struct.pack('!BH', setting.bright, colorVal))

	# 	if setting.hasGradient:
	# 		self.connection.sendBytes(struct.pack('!BBBBB', setting.rbright & 0xff, setting.dbright & 0xff, setting.db & 0xff, setting.dg & 0xff, setting.dr & 0xff))

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

			else:
				return -1

	def waitForFree(self):
		while True:
			response = self.connection.receiveBytes(1)
			if len(response) == 0:
				continue

			code = struct.unpack('!B', response[0])[0]
			if code == 0x81:
				return True

			return False

	def sendAndWait(self, data):
		while True:
			self.connection.sendBytes(data)
			status = self.getStatus()
			if status <= 0:
				break
			if not self.waitForFree():
				status = -2
				break

		return status		

	def sendTimeReset(self, atTime):
		return self.sendAndWait(struct.pack('!BH', 1, atTime))

	def sendLightUpdate(self, atTime, addr, bright, r, g, b):
		lowByte = (g << 4) | r
		midByte = ((bright & 0xf) << 4) | b
		highByte = ((addr & 0xf) << 4) | (bright >> 4)
		topByte = 0x80 | (addr >> 6)

		return self.sendAndWait(struct.pack('!BHBBB', topByte, atTime, highByte, midByte, lowByte))

	# def sendAtTime(self, commandList, time, resetAtEnd=False):
	# 	while True:
	# 		cmdByte = 0x20
	# 		if resetAtEnd:
	# 			cmdByte |= 0x10
	# 		self.connection.sendBytes(struct.pack('!BH', cmdByte, time))
	# 		for command in commandList:
	# 			if command.type == 'change':
	# 				self.changeLights(command.addressList, command.color)
	# 			elif command.type == 'settime':
	# 				self.connection.sendBytes(struct.pack('!BH', 0x90, command.time))

	# 		self.connection.sendBytes(struct.pack('!B', 0))
	# 		status = self.getStatus()

	# 		if status <= 0:
	# 			break

	# 		if not self.waitForFree():
	# 			status = -2
	# 			break

	# 	return status

	def sendClear(self, waitForStatus=True):
		self.connection.sendBytes(struct.pack('!B', 0))
		if waitForStatus: # At first launch, don't bother with status, since we need to drain bytes anyway
			return self.getStatus()

	def drainBytes(self):
		while len(self.connection.receiveBytes(1)) > 0:
			pass

