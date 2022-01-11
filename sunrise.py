import math
import random
import time
import neopixel 
import board

# LED strip configuration:
pix_trees = list(range(104, 168))
LED_COUNT = len(pix_trees)
BLACK = (0, 0, 0)

ASTRO_DAWN = -100
#DARK_SKY = (50, 70, 200) 
DARK_SKY = (25, 35, 100) 

CIVIL_DAWN = -50
#BRIGHT_SKY = (200, 70, 200)
BRIGHT_SKY = (100, 35, 100)

SUNRISE = 0
SUN_JUST_UP = (255, 190, 70)

DAY = LED_COUNT / 4
SUN_FULL_UP = (255, 255, 100)

pin = board.D18
pixels = neopixel.NeoPixel(pin, 300, auto_write=False)

def colorWipe(color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(LED_COUNT):
        pixels[pix_trees[i]] = color
        pixels.show()
        time.sleep(wait_ms/1000.0)

def semicircle(offset):
    semi = []
    r = LED_COUNT/2
    for x in range(LED_COUNT):
        semi.append(math.sqrt(r**2 - (x-r)**2) + offset)
    return semi

def interpolateColor(startColor, startVal, endColor, endVal, position):
    timeDist = endVal - startVal
    timePercent = (position - startVal) / timeDist
    interpColor = []
    for i in range(3):
        interpColor.append(int(startColor[i] + (endColor[i] - startColor[i]) * timePercent))

    return tuple(interpColor)

class sunManager():
    def __init__(self, strip, sunrise=True):
        self.sunrise = sunrise
        self.strip = strip
        self.sun = semicircle(offset=-100-LED_COUNT/2) #Top of sun at ~ -100

    def update(self): 
        colors = []
        for x in range(len(self.strip)):
            self.sun[x] += 1
        for y in self.sun:
            if y < ASTRO_DAWN:
                colors.append(BLACK)
            elif y < CIVIL_DAWN:
                colors.append(interpolateColor(BLACK, ASTRO_DAWN, DARK_SKY, CIVIL_DAWN, y))
            elif y < SUNRISE:
                colors.append(interpolateColor(DARK_SKY, CIVIL_DAWN, BRIGHT_SKY, SUNRISE, y))
            elif y < DAY:
                colors.append(interpolateColor(SUN_JUST_UP, SUNRISE, SUN_FULL_UP, DAY, y))
            else:
                colors.append(SUN_FULL_UP)
            print(y, colors[-1])

        print(colors)
        for x, c in enumerate(colors):
            pixels[self.strip[x]]=(c[0], c[1], c[2])
        pixels.show()

if __name__ == "__main__":
    testsunmanager = sunManager(pix_trees)
    while(True):
        try:
            testsunmanager.update()
            time.sleep(0.05)
        except KeyboardInterrupt:
            colorWipe((0,0,0), 10)
            break
