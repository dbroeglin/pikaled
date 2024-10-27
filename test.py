#!/usr/bin/env python
import time
import sys
import random

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics

from PIL import Image, ImageDraw, ImageFont

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 16
options.cols = 32
options.chain_length = 6
options.gpio_slowdown = 3
options.parallel = 2
#options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
options.multiplexing = 4

matrix = RGBMatrix(options = options)
offset_canvas = matrix.CreateFrameCanvas()

states = [random.choice(["miss", "hit", "unknown"]) for _ in range(options.chain_length * 2)]
matrix.Clear()
pikaled = PikaLed()

while True:
    for participant_nb in range(9):
        for i, state, in enumerate(states):
            pikaled.display_result(offset_canvas, state, participant_nb, i)

    offset_canvas = matrix.SwapOnVSync(offset_canvas)
    time.sleep(1)
