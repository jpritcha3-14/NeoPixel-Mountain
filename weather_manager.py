import argparse
import time
from multiprocessing import Process, Pipe

from pyowm import OWM 
import neopixel, board

from rain_snow import (
    Intensity,
    RainSnow,
)

from twinkling_stars import TwinklingStars

pin = board.D18
pixels = neopixel.NeoPixel(pin, 300, auto_write=False)
pix_rain = list(range(57))


def clear_pixels():
    for i in pix_rain:
        pixels[i] = (0, 0, 0)

class DummyWeatherClass():

    def __init__(self, rain=None, snow=None):
        self._rain = {} if rain == None else rain
        self._snow = {} if snow == None else snow

    @property 
    def rain(self):
        return self._rain

    @property 
    def snow(self):
        return self._snow

    @property 
    def srise_time(self):
        return 0 

    @property 
    def sset_time(self):
        return 0 


class WeatherManager():
    def __init__(self, pixels, tick_time=0.05, fade_ticks=100):
        self.pixels = pixels
        self.tick_time = tick_time
        self.fade_ticks = fade_ticks 
        self.cur_sky = None
        self.cur_ground = None
        self.next_sky = None
        self.next_ground = None
        self.change_sky = False
        self.change_ground = False
        self.fade_sky = 0 
        self.fade_ground = 0

    def update_weather(self, cur_weather):
        if cur_weather.snow:
            print("setting snow")
            self.next_sky = RainSnow(
                amount = cur_weather.snow.get("1h", 0.05),
                snow = True
            )
            self.fade_sky = self.fade_ticks
        elif cur_weather.rain:
            print("setting rain")
            self.next_sky = RainSnow(
                amount = cur_weather.rain.get("1h", 0.05),
                snow = False
            )
            self.fade_sky = self.fade_ticks
        elif (time.time() > cur_weather.sset_time 
              or time.time() < cur_weather.srise_time):
            self.next_sky = TwinklingStars()
            self.fade_sky = self.fade_ticks
        else: 
            # No weather
            self.next_sky = None

        print(cur_weather.rain, cur_weather.snow, self.next_sky, self.cur_sky)

    def tick(self):
        print("fade_ticks", self.fade_sky)
        clear_pixels()
        pixel_updates = {}
        # Get pixel values for current weather event
        if self.cur_sky:
            pixel_updates.update(self.cur_sky.update()) 

        # Use current weather event
        if self.fade_sky == 0:
            for k, v in pixel_updates.items():
                self.pixels[k] = v

        # Fade out and transition to next weather event
        else:
            for k, v in pixel_updates.items():
                self.pixels[k] = tuple(
                    map(
                        lambda x: max(0, x-(self.fade_ticks - self.fade_sky)), v
                    )
                )
            self.fade_sky -= 1
            if self.fade_sky == 0:
                self.cur_sky = self.next_sky
                self.next_sky = None

        self.pixels.show()
        time.sleep(self.tick_time)


def current_weather_process(conn):
    with open("weather.key", "r") as f:
        key = f.read().strip()

    with open("zip.txt", "r") as f:
        zipcode = f.read().strip()

    owm = OWM(key)
    mgr = owm.weather_manager()

    while True:
        observation = mgr.weather_at_zip_code(zipcode, "us")
        w = observation.weather
        print(w.rain, w.snow)
        conn.send(w)

        time.sleep(10)

def dummy_weather_process(conn):
    while True:
        conn.send(DummyWeatherClass(rain={"1h": 0.5}))
        time.sleep(10)
        conn.send(DummyWeatherClass(snow={"1h": 0.5}))
        time.sleep(10)
        conn.send(DummyWeatherClass())
        time.sleep(10)


def update_leds_process(child_process):
    wm = WeatherManager(pixels)
    parent_conn, child_conn = Pipe()
    p = Process(target=child_process, args=(child_conn,))
    p.start()

    time.sleep(1)
    while True:
        if parent_conn.poll():
            wm.update_weather(parent_conn.recv())
        wm.tick()
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', dest='test', action='store_true')
    args = parser.parse_args()

    update_leds_process(dummy_weather_process if args.test else current_weather_process)

