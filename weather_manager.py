import time
from pyowm import OWM 

with open("weather.key", "r") as f:
    key = f.read().strip()

owm = OWM(key)
mgr = owm.weather_manager()

while True:
    observation = mgr.weather_at_zip_code("97214", "us")
    w = observation.weather

    print(time.strftime('%Y-%m-%dT%H:%M:%SZ',
        time.localtime(time.time())))
    print(w.precipitation_probability)
    print(w.rain)

    with open("data.txt", "a") as f:
        f.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(time.time())) + "\n")
        f.write(str(w.precipitation_probability) + "\n")
        f.write(str(w.rain) + "\n")
                                
    time.sleep(10) 
