import interfaceIO
import struct

class SerialInterface(object):

	def __init__(self, port):
		self.connection = interfaceIO.InterfaceIO(port, 3)

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
		print("Buffer full")
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

	def sendLightUpdate(self, atTime, addr, color):
		lowByte = (color.g << 4) | color.r
		midByte = ((color.bright & 0xf) << 4) | color.b
		highByte = ((addr & 0xf) << 4) | (color.bright >> 4)
		topByte = 0x80 | (addr >> 4)

		return self.sendAndWait(struct.pack('!BHBBB', topByte, atTime, highByte, midByte, lowByte))

	def sendMessage(self, message, atTime):
		if message.type == 'cleartime':
			return self.sendTimeReset(atTime)
		elif message.type == 'change':
			return self.sendLightUpdate(atTime, message.address, message.color)
		return -1

	def sendClear(self, waitForStatus=True):
		self.connection.sendBytes(struct.pack('!B', 0))
		if waitForStatus: # At first launch, don't bother with status, since we need to drain bytes anyway
			return self.getStatus()

	def drainBytes(self):
		while len(self.connection.receiveBytes(1)) > 0:
			pass
