#!/usr/bin/env python
import time
import sys
import random

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics

from PIL import Image, ImageDraw, ImageFont
from pikaled import PikaLed


import os

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 16
options.cols = 32
options.chain_length = 6
options.gpio_slowdown = 3
options.parallel = 3
options.multiplexing = 4

matrix = RGBMatrix(options = options)
offset_canvas = matrix.CreateFrameCanvas()

matrix.Clear()

url = os.getenv('PIKAICHU_URL') or 'http://localhost:3000/scoreboard/dummy.json'
pikaled = PikaLed(canvas=offset_canvas, url=url, matrix=matrix)

while True:
    pikaled.update()
    time.sleep(1)
