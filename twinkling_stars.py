#/bin/python3

import argparse
import neopixel, board
import time
import random
import math

pix_stars = list(range(57, 104)) + [1, 3, 5, 7, 9]
pin = board.D18
pixels = neopixel.NeoPixel(pin, 300, auto_write=False)
MAX_NUM_STARS = 20

def clear_pixels():
    for i in pix_stars:
        pixels[i] = (0, 0, 0)

def interpolate(start, end, steps, integer=False):
    diff = (end - start) / steps
    result = [start]
    cur_val = start
    for x in range(steps):
        cur_val += diff
        result.append(cur_val)
    if integer:
        result = list(map(math.floor, result))
    return result

class Star:
    def __init__(self, num, ticks=0, oscillations=0, intensity=0, offset=0):
        self.num = num
        self.ticks = ticks 
        self.oscillations = oscillations
        self.intensity = intensity
        self.offset = offset
        self.done = False
        self.linear_interp = interpolate(
            start=0, 
            end=self.offset, 
            steps=60,
            integer=True, 
        )
        self.sin_interp = interpolate(
            start=0, 
            end=(self.oscillations*2+1)*math.pi,
            steps=self.ticks,
        )
        self.iter = iter(self)

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
        
       
class TwinklingStars():

    def __init__(self):
        self.active_stars = []

    def update(self):
        #Add stars to active stars to maintain the MAX number in avtive_stars
        print(list(map(lambda x: x.num, self.active_stars)))
        while len(self.active_stars) < MAX_NUM_STARS:
            num = random.choice(
                    list(
                        set(pix_stars) - set(map(lambda x: x.num, self.active_stars))
                    )
                )
            ticks = random.randint(100, 400)
            oscillations = random.randint(
                math.floor(ticks/100),
                math.floor(ticks/100)+2
            )
            offset = random.randint(10, 40)
            intensity = random.randint(
                math.floor(offset/4), 
                math.floor(offset/2),
            )
            self.active_stars.append(
                Star(
                    num=num,
                    ticks=ticks,
                    oscillations=oscillations,
                    intensity=intensity,
                    offset=offset,
                )
            )

        # Update star pixel values and show
        star_values = {}
        for s in self.active_stars:
            cur_val = next(s.iter)
            star_values[s.num] = (cur_val, cur_val, cur_val)

        # Remove stars that have finished twinkling
        for i in reversed(range(len(self.active_stars))):
            if self.active_stars[i].done:
                self.active_stars.pop(i)

        return star_values

