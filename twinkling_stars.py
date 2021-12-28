#/bin/python3

import argparse
import neopixel, board
import time
import random
import math

pix_stars = list(range(57, 134))
pin = board.D18
pixels = neopixel.NeoPixel(pin, 300, auto_write=False)

def clear_pixels():
    for i in pix_rain:
        pixels[i] = (0, 0, 0)

def interpolate(start, end, steps, integer=False):
    diff = (end - start) / steps
    if integer:
        diff = math.floor(diff)
    result = [start]
    cur_val = start
    for x in range(steps):
        cur_val += diff
        result.append(cur_val)
    return result

class Star:
    def __init__(self, ticks=0, oscillations=0, intensity=0, offset=0):
        self.ticks = ticks 
        self.oscillations = oscillations
        self.intensity = intensity
        self.offset = offset
        self.done = False
        self.linear_interp = interpolate(
            start=0, 
            end=self.offset, 
            steps=10,
            integer=True, 
        )
        self.sin_interp = interpolate(
            start=0, 
            end=(self.oscillations*2+1)*math.pi,
            steps=self.ticks,
        )

    def __iter__(self):
        for i in range(1, len(self.linear_interp)):
            yield self.linear_interp[i]

        for j in range(len(self.sin_interp)):
            yield math.floor(
                self.intensity * math.sin(self.sin_interp[j]) + self.offset
            )

        for k in reversed(range(1, len(self.linear_interp))):
            yield self.linear_interp[k]

        self.done = True
        yield 0
        
def main():
    pass

if __name__ == '__main__':
    test = Star(ticks=70, oscillations=2, intensity=15, offset=50)
    for x in test:
        print(x)
    """
    try:
        main()
    # Clear pixels on SIGINT
    except KeyboardInterrupt:
        clear_pixels()
        pixels.show()
    """
