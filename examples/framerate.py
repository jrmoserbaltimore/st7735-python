# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time
import math
import sys

from PIL import Image
from PIL import ImageDraw
import ST7735 as ST7735

if sys.implementation.name == "micropython":
    from machine import Pin
    from machine import SPI
else:
    # Use gpizero and spidev
    from gpiozero import OutputDevice
    import spidev

SPI_SPEED_MHZ = 10  # Higher speed = higher framerate

if len(sys.argv) > 1:
    SPI_SPEED_MHZ = int(sys.argv[1])

print("""
framerate.py - Test LCD framerate.

If you're using Breakout Garden, plug the 0.96" LCD (SPI)
breakout into the rear slot.

Running at: {}MHz
""".format(SPI_SPEED_MHZ))

if sys.implementation.name == "micropython":
    # Hardware SPI device
    spi = machine.SPI(0)
    sck = machine.Pin(18)
    smosi = machine.Pin(19)
    smiso = machine.pin(20)
    scs = machine.pin(21)
    spi.init(baudrate=SPI_SPEED_MHZ * 1000000, sck=sck, mosi=smosi, miso=smiso)
    dc = machine.Pin(2)
    backlight = machine.Pin(3)
else:
    # Set up the spidev device
    spi = spidev.SpiDev(0, ST7735.BG_SPI_CS_FRONT)
    spi.mode = 0
    spi.lsbfirst = False
    spi.max_speed_hz = SPI_SPEED_MHZ * 1000000
    # add the send() method as alias to xfer3()
    spi.send = spi.xfer3
    # gpiozero pins
    dc = OutputDevice(9)
    backlight = OutputDevice(19)
# Create ST7735 LCD display class.
disp = ST7735.ST7735(
    port=spi,
    dc=dc,
    backlight=backlight,               # 18 for back BG slot, 19 for front BG slot.
    rotation=90,
)

WIDTH = disp.width
HEIGHT = disp.height
STEPS = WIDTH * 2
images = []

for step in range(STEPS):
    image = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 128))
    draw = ImageDraw.Draw(image)

    if step % 2 == 0:
        draw.rectangle((79, 0, 159, 79), (0, 128, 0))
    else:
        draw.rectangle((0, 0, 79, 79), (0, 128, 0))

    f = math.sin((float(step) / STEPS) * math.pi)
    offset_left = int(f * WIDTH)
    draw.ellipse((offset_left, 35, offset_left + 10, 45), (255, 0, 0))

    images.append(image)

count = 0
time_start = time.time()

while True:
    disp.display(images[count % len(images)])
    count += 1
    time_current = time.time() - time_start
    if count % 120 == 0:
        print("Time: {:8.3f},      Frames: {:6d},      FPS: {:8.3f}".format(
            time_current,
            count,
            count / time_current))
