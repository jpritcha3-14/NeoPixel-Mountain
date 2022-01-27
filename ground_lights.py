#/bin/python3

import argparse
import neopixel, board
import time
import random
import math

pix_trees = list(range(104, 160))
pix_mountains = list(range(160, 235))
pin = board.D18
pixels = neopixel.NeoPixel(pin, 300, auto_write=False)
MAX_NUM_LIGHTS = 10

def clear_pixels(pix_range):
    for i in pix_range:
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

class Light:
    def __init__(self, num, ticks=0, oscillations=0, intensity=0):
        self.num = num
        self.ticks = ticks 
        self.oscillations = oscillations
        self.intensity = intensity
        self.done = False
        self.cos_interp = interpolate(
            start=0, 
            end=(self.oscillations*2)*math.pi,
            steps=self.ticks,
        )
        self.iter = iter(self)

    def __iter__(self):
        for i in range(len(self.cos_interp)):
            yield math.floor(
                self.intensity * (1 - math.cos(self.cos_interp[i]))
            )

        self.done = True
        yield 0
        
def main(pix_range, color):
    active_lights = []
    while True:
        #Add lights to active lights to maintain the MAX number in avtive_lights
        #print(list(map(lambda x: x.num, active_lights)))
        while len(active_lights) < MAX_NUM_LIGHTS:
            num = random.choice(
                    list(
                        set(pix_range) - set(map(lambda x: x.num, active_lights))
                    )
                )
            ticks = random.randint(100, 400)
            oscillations = random.randint(
                math.floor(ticks/100),
                math.floor(ticks/100)+2
            )
            intensity = random.randint(30, 100)
            active_lights.append(
                Light(
                    num=num,
                    ticks=ticks,
                    oscillations=oscillations,
                    intensity=intensity,
                )
            )

        clear_pixels(pix_range)

        # Update light pixel values and show
        for s in active_lights:
            cur_val = next(s.iter)
            pixels[s.num] = tuple(math.floor(x * cur_val) for x in color)
        print(pixels[104:160])
        pixels.show()

        # Remove lights that have finished twinkling
        for i in reversed(range(len(active_lights))):
            if active_lights[i].done:
                active_lights.pop(i)

        time.sleep(0.05)

        
class GroundLights():

    def __init__(self, pix_range, color):
        self.active_lights = []
        self.pix_range = pix_range
        self.color = color

    def update(self):
        #Add lights to active lights to maintain the MAX number in avtive_lights
        print(list(map(lambda x: x.num, self.active_lights)))
        while len(self.active_lights) < MAX_NUM_LIGHTS:
            num = random.choice(
                    list(
                        set(pix_range) - set(map(lambda x: x.num, self.active_lights))
                    )
                )
            ticks = random.randint(100, 400)
            oscillations = random.randint(
                math.floor(ticks/100),
                math.floor(ticks/100)+2
            )
            intensity = random.randint(
                math.floor(offset/4), 
                math.floor(offset/2),
            )
            self.active_lights.append(
                Light(
                    num=num,
                    ticks=ticks,
                    oscillations=oscillations,
                    intensity=intensity,
                )
            )

        # Update light pixel values and show
        light_values = {}
        for s in self.active_lights:
            cur_val = next(s.iter)
            light_values[s.num] = tuple(math.floor(x * cur_val) for x in self.color)

        # Remove lights that have finished twinkling
        for i in reversed(range(len(self.active_lights))):
            if self.active_lights[i].done:
                self.active_lights.pop(i)

        return light_values


if __name__ == '__main__':
    try:
        main(pix_trees, (0, 1, 0))
    # Clear pixels on SIGINT
    except KeyboardInterrupt:
        clear_pixels()
        pixels.show()