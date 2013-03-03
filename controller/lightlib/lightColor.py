MAX_BRIGHT = 0xcc
MAX_COLOR = 0xd * 3

class Color(object):
	"""Represents the color of an individual light"""

	def __init__(self, bright, r, g, b, forceBright=False):
		"""
		bright: brightness, from 0 to 204
		r,g,b: color values from 0 to 15, such that the total does
			not exceed 39
		forceBright: true if the brightness should jump to the new
			value. This may cause a temporary glitch. Otherwise
			the brightness fades up/down
		"""
		self.bright = bright
		self.forceBright = forceBright
		self.r = r
		self.g = g
		self.b = b
		self.normalize()
		self.computeColorGradient = True
		self.computeBrightGradient = True

	def normalize(self):
		"""Ensures that brightness and color are within the limits"""
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
		"""Compares two colors"""
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
