import interfaceIO
import lightColor
import struct

class LightError(Exception):
	"""An exception class used to handle errors
	in communicating with the lights
	"""
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return "LightError: " + repr(self.value)

class ColorChangeMessage(object):
	"""A message that causes the color of a light with
	a given address to change"""
	def __init__(self, address, color):
		self.type = 'change'
		self.address = address
		self.color = color

class TimeMessage(object):
	"""A message that resets the light timer"""
	def __init__(self):
		self.type = 'cleartime'

class SerialInterface(object):
	"""Provides an interface to send individual messages
	to the lights
	"""

	def __init__(self, port):
		"""Creates an interface using the given serial port"""
		self.connection = interfaceIO.InterfaceIO(port, 3)


	def sendMessage(self, message, atTime):
		"""Puts a message that should activate at a given time
		into the lights' input buffer
		"""
		if message.type == 'cleartime':
			return self.sendTimeReset(atTime)
		elif message.type == 'change':
			return self.sendLightUpdate(atTime, message.address, message.color)
		raise LightError("Invalid message type")

	def sendClear(self, waitForStatus=True):
		"""Clears the lights' input buffer"""
		self.connection.sendBytes(struct.pack('!B', 0))
		if waitForStatus: # At first launch, don't bother with status, since we need to drain bytes anyway
			status = self.getStatus()
			if status != 0:
				raise LightError("Couldn't clear buffer, status: %d" % status)

	def drainBytes(self):
		"""Removes any bytes that may be waiting in the USB buffer"""
		while len(self.connection.receiveBytes(1)) > 0:
			pass


	# Methods below here probably won't be used by other modules (but I'm not trying to hide them either)
	def sendTimeReset(self, atTime):
		"""Sends a message to clear the light timer at atTime"""
		status = self.sendAndWait(struct.pack('!BH', 1, atTime))
		if status != 0:
			raise LightError("Couldn't send time reset, status: %d" % status)

	def sendLightUpdate(self, atTime, addr, color):
		"""Sends a message to change the color of the light with address addr at atTime"""
		lowByte = (color.g << 4) | color.r
		midByte = ((color.bright & 0xf) << 4) | color.b
		highByte = ((addr & 0xf) << 4) | (color.bright >> 4)
		topByte = 0x80 | (addr >> 4)

		status = self.sendAndWait(struct.pack('!BHBBB', topByte, atTime, highByte, midByte, lowByte))
		if status != 0:
			raise LightError("Couldn't send update, status: %d" % status)

	def sendAndWait(self, data):
		"""Sends a message and then waits until the ack, and retries until
		the input buffer has space. Returns the error code from the lights
		"""
		while True:
			self.connection.sendBytes(data)
			status = self.getStatus()
			if status <= 0:
				break
			if not self.waitForFree():
				status = -2
				break

		return status

	def getStatus(self):
		"""Gets the ack/nack status from the lights after sending a message.
		A return value of 0 indicates success, 1 indicates a full input
		buffer, and -1 indicates an error"""
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
		"""Blocks until the lights send a signal indicating that the input
		buffer is ready to accept more data"""
		print("Buffer full")
		while True:
			response = self.connection.receiveBytes(1)
			if len(response) == 0:
				continue

			code = struct.unpack('!B', response[0])[0]
			if code == 0x81:
				return True

			return False

