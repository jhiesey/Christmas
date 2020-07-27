import pyaudio
import time
import array
import numpy
import math
import threading
from lightlib.abstractLightController import *

audio = pyaudio.PyAudio()

SAMPLE_RATE = 44100
WINDOW_SIZE = 4096
FIRST_BUCKET = 80
LAST_BUCKET = 2000
NUM_BUCKETS = 51
BUCKET_RATIO = pow(LAST_BUCKET/FIRST_BUCKET, 1.0/NUM_BUCKETS)
window = numpy.hanning(WINDOW_SIZE)

freqs = numpy.fft.rfftfreq(WINDOW_SIZE, 1.0/SAMPLE_RATE)# * 2 - 1, 1.0/SAMPLE_RATE)

normalized = None
normalized_sema = threading.Semaphore(0)
mags = None
def on_data(in_data, frame_count, time_info, status_flags):
	global normalized, mags
	data = array.array('f')
	data.fromstring(in_data)
	transformed = numpy.fft.rfft(data) #numpy.convolve(numpy.array(data), window))
	mags = numpy.absolute(transformed)

	# tuple is sum, count
	buckets = [(0, 0) for i in xrange(NUM_BUCKETS)]
	for i, mag in enumerate(mags):
		freq = freqs[i]
		if freq < FIRST_BUCKET:
			continue
		if freq > LAST_BUCKET:
			break

		bucket = int(math.log(freq / FIRST_BUCKET, BUCKET_RATIO))
		if bucket < 0:
			continue
		if bucket >= len(buckets):
			break
		total, count = buckets[bucket]
		buckets[bucket] = (total + mag * freq, count + 1)

	normalized = [(FIRST_BUCKET * pow(BUCKET_RATIO, i + 0.5), math.log10(total)) for (i, (total, count)) in enumerate(buckets) if count != 0]
	normalized_sema.release()
	return (None, pyaudio.paContinue)


stream = audio.open(format=pyaudio.paFloat32, rate=SAMPLE_RATE, channels=1, input=True, frames_per_buffer=WINDOW_SIZE, stream_callback=on_data)

MAX_BRIGHT = 0xd
OFF_VOLUME = -1
ON_VOLUME = 3

# # while True:
# # 	normalized_sema.acquire()

# import matplotlib.pyplot as plt

# plt.ion()

# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.axis([0, 2000, -6, 6])

# line = None

# while True:
# 	normalized_sema.acquire()
# 	# unzipped = zip(*list(normalized))
# 	mags2 = list(mags)

# 	xs = freqs
# 	ys = [math.log10(max(mag, 0.01)) for (i, mag) in enumerate(mags2)]

# 	# plt.clear()
# 	# ax.clear()
# 	if not line:
# 		line, = ax.plot(xs, ys, 'r-')
# 		# plt.draw()
# 		# plt.show()
# 	else:
# 		line.set_ydata(ys)
# 		fig.canvas.draw()

# 	# ax.show()




class SpectrumController(AbstractLightController):
	def __init__(self, port):
		super(SpectrumController, self).__init__(port, 0, 0, 0, True)

	def waitForRealTime(self):
		normalized_sema.acquire()
		self.raw_data = list(normalized)

	def colorListUpdate(self, currTime, colors):
		print 'updating'
		print len(colors)
		print len(self.raw_data)
		for i, color in enumerate(colors):
			freq, amplitude = self.raw_data[i]
			brightness = min(max((amplitude - OFF_VOLUME) / (ON_VOLUME - OFF_VOLUME), 0), 1) * MAX_BRIGHT
			color.r = color.g = color.b = brightness

controller = SpectrumController('/dev/tty.usbmodem1411')
controller.runUpdate()
