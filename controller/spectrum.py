#!/usr/bin/env python

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

stream = None

MAX_BRIGHT = 0xd
OFF_VOLUME = 2
ON_VOLUME = 6

def getColor(index):
	if index <= 0:
		return (13, 0, 0)
	elif index == 1:
		return (11, 1, 0)
	elif index == 2:
		return (13, 7, 0)
	elif index == 3:
		return (1, 13, 0)
	elif index == 4:
		return (0, 1, 13)
	elif index == 5:
		return (2, 0, 13)
	elif index >= 6:
		return (8, 0, 13)

def interpolateColor(color, index):
	lowIndex = math.floor(index)
	highFraction = index % 1
	(lowR, lowG, lowB) = getColor(lowIndex)
	(highR, highG, highB) = getColor(lowIndex + 1)
	color.r = highR * highFraction + lowR * (1 - highFraction)
	color.g = highG * highFraction + lowG * (1 - highFraction)
	color.b = highB * highFraction + lowB * (1 - highFraction)

class SpectrumController(AbstractLightController):
	def __init__(self, port):
		super(SpectrumController, self).__init__(port, 0, 0, 0, True)

	def waitForRealTime(self):
		global stream
		if stream is None:
			stream = audio.open(format=pyaudio.paFloat32, rate=SAMPLE_RATE, channels=1, input=True, frames_per_buffer=WINDOW_SIZE)
		rawData = stream.read(WINDOW_SIZE)
		data = array.array('f')
		data.fromstring(rawData)
		transformed = numpy.fft.rfft(data)
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
		self.raw_data = list(normalized)

	def colorListUpdate(self, currTime, colors):
		for i, color in enumerate(colors):
			freq, amplitude = self.raw_data[i] if i < len(self.raw_data) else (0, 0)
			index = 6 - min(max((amplitude - OFF_VOLUME) / (ON_VOLUME - OFF_VOLUME), 0), 1) * 6
			interpolateColor(color, index)

controller = SpectrumController('/dev/tty.usbmodem1411')
controller.runUpdate()
