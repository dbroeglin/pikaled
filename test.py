#!/usr/bin/env python
import time
import sys
import random

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics

from PIL import Image, ImageDraw, ImageFont
from pikaled import PikaLed


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

matrix.Clear()
pikaled = PikaLed(canvas=offset_canvas, url='http://localhost:3000/scoreboard/dummy.json', matrix=matrix)

while True:
    pikaled.update()
    time.sleep(1)
