#/bin/python3

import argparse
import neopixel, board
import time
import random
from enum import Enum

pix_rain = list(range(57))
pix_streaks = []
pix_streaks.append(list(reversed(range(4))))
pix_streaks.append([4, 5, 6, 7, 8, 9])
pix_streaks.append([15, 14, 13, 12, 11, 10])
pix_streaks.append([16, 17, 18, 19, 20, 21, 22, 23])
pix_streaks.append([27, 26, 25, 24])
pix_streaks.append([28, 29, 30, 31, 32, 33, 34])
pix_streaks.append([40, 39, 38, 37, 36, 35])
pix_streaks.append([41, 42, 43, 44, 45, 46])
pix_streaks.append([51, 50, 49, 48, 47])
pix_streaks.append([52, 53, 54, 55, 56])
pix_stars = list(range(57, 134))
pix_trees = list(range(104, 160))
pix_mountains = list(range(160, 235))
pin = board.D18
pixels = neopixel.NeoPixel(pin, 300, auto_write=False)
MAX_ACTIVE_STREAKS = 5

class Intensity(Enum):
    LIGHT = 3
    MEDIUM = 5
    HEAVY = 7

def clear_pixels():
    for i in pix_rain:
        pixels[i] = (0, 0, 0)

class PixStreak:
    
    def __init__(self, pix_idx, pix_list, snow=False):
        self.pix_idx = pix_idx
        self.pix_list = pix_list
        self.snow = snow
        self.speed = random.randint(5, 8) if self.snow else random.randint(1, 4)
        self.LowLight = 25
        self.HighLight = 75
        self.index = 0
        self.tick = -1 
        self.pixels = (0, 0, 0)
        self.done = False 
        
    def __iter__(self):
        return self

    # This function allows us to iterate through the streak state, returning
    # the next set of lit up pixels on each call to next(), while hiding the
    # messy details of how these are being calculated inside the class.  From
    # the outside when we use the PixStreak class, all we have to do is create
    # an object from it, get the pixels with next(), and check if it's "done".
    def __next__(self):
        if self.index >= len(self.pix_list):
            self.done = True
            raise StopIteration
        
        # Increase the tick count for this streak, modulo the speed
        self.tick = (self.tick + 1) % self.speed

        # If the tick count isn't 0, just return the current pixel state
        if self.tick != 0:
            return self.pixels

        # Otherwise, update the current pixels before returning
        if self.index == 0:
            self.pixels = { 
                self.pix_list[0]: (self.LowLight if self.snow else 0,
                                   self.LowLight if self.snow else 0,
                                   self.LowLight),
            }
        elif self.index == len(self.pix_list) - 1:
            self.pixels = { 
                self.pix_list[-2]: (self.LowLight if self.snow else 0, 
                                    self.LowLight if self.snow else 0, 
                                    self.LowLight),
                self.pix_list[-1]: (self.HighLight if self.snow else 0,
                                    self.HighLight if self.snow else 0,
                                    self.HighLight),
            }
        else:
            self.pixels = { 
                self.pix_list[self.index-1]: (self.LowLight if self.snow else 0,
                                              self.LowLight if self.snow else 0,
                                              self.LowLight),
                self.pix_list[self.index]: (self.HighLight if self.snow else 0,
                                            self.HighLight if self.snow else 0,
                                            self.HighLight),
                self.pix_list[self.index+1]: (self.LowLight if self.snow else 0,
                                              self.LowLight if self.snow else 0,
                                              self.LowLight),
            }

        self.index += 1
        return self.pixels


class RainSnow():

    def __init__(self, amount=0.05, snow=False):
        self.active_streaks=[]
        self.snow=snow
        self.intensity=self.get_intensity(amount)

    def get_intensity(self, val):
        if self.snow:
            if val < 0.1:
                return Intensity.LIGHT
            elif val < 0.3:
                return Intensity.MEDIUM
            else:
                return Intensity.HEAVY
        else:
            if val < 0.2:
                return Intensity.LIGHT
            elif val < 0.5:
                return Intensity.MEDIUM
            else:
                return Intensity.HEAVY

    def update(self):
        while True:
            # Append new random PixStreaks to self.active_streaks until there are
            # self.intensity 
            while len(self.active_streaks) < self.intensity.value:
                # Get a new streak number that isn't already in self.active_streaks
                new_streak_number = random.choice(
                    list(
                        set(range(len(pix_streaks)))-set(map(lambda x: x.pix_idx, self.active_streaks))
                    )
                )
                self.active_streaks.append(
                    PixStreak(
                        new_streak_number,
                        pix_streaks[new_streak_number], 
                        self.snow,
                    )
                )

            # For each active streak, get its next pixel value
            pixel_list = []
            for s in self.active_streaks:
                try:
                    pixel_list.append(next(s))
                except StopIteration:
                    print("{} streak {} finished".format("snow" if self.snow else "rain", s.pix_idx))

            print(pixel_list)
            # Remove any streaks that have finished from the active_streaks queue
            # The range is reversed to prevent shifing list elements before popping them
            for n in reversed(range(self.intensity.value)):
                if self.active_streaks[n].done:
                    self.active_streaks.pop(n)

            # unpack list into dictionary 
            pixel_updates = {}
            for d in pixel_list:
                print(d)
                pixel_updates.update(d)

            return pixel_updates

