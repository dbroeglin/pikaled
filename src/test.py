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
options.chain_length = 18 
options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
options.multiplexing = 4

gray=(100,100,100)
black=(0,0,0)

font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 20)


hit = Image.new("RGB", (16, 16))  # Can be larger than matrix if wanted!!
draw = ImageDraw.Draw(hit)  # Declare Draw instance before prims
draw.ellipse([(1,1), (14, 14)], fill=(0,0,0), outline=gray, width=2)

miss = Image.new("RGB", (16, 16))  # Can be larger than matrix if wanted!!
draw = ImageDraw.Draw(miss)  # Declare Draw instance before prims
draw.line([(0, 0), (14, 14)], fill=gray, width=2)
draw.line([(0, 15), (15, 0)], fill=gray, width=2)
draw.rectangle([(0, 0), (15, 15)], fill=None, outline=black, width=1)

unknown = Image.new("RGB", (16, 16))  # Can be larger than matrix if wanted!!
draw = ImageDraw.Draw(unknown)  # Declare Draw instance before prims
draw.text((7, 7), "?", font=font, anchor="mm", features=["-kern"])

matrix = RGBMatrix(options = options)
offset_canvas = matrix.CreateFrameCanvas()

states = [random.choice([miss, hit, unknown]) for _ in range(options.chain_length * 2)]
while True:
    for n in range(-16, 128):  # Start off top-left, move off bottom-right
        matrix.Clear()
        for i, state, in enumerate(states):
            matrix.SetImage(state, 16 * i, 0)
        time.sleep(1)    

    offset_canvas = matrix.SwapOnVSync(offset_canvas)

