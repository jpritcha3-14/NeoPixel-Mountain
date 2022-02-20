# NeoPixel real-time weather art project


## Goal

Depict real-time weather events using the [OpenWeather API](https://openweathermap.org/api) on a custom built art project using a Raspberry Pi to interface strands of addressable [Adafruit NeoPixel LEDs](https://www.adafruit.com/product/1138?length=1).

## Usage
Make sure the following two files are in the project directory and contain the OpenWeather API key and the operating zip code respectively:
```
weather.key
zip.txt
```
Run the following command to start the LED display process and weather API subprocess:

`sudo python3 weather_manager.py [--test]`

The  optional `--test` flag uses a dummy weather subprocess instead of the weather API subprocess.  It cycles through different weather events every 15 seconds.

While the code is specific to the NeoPixel address ranges used on this custom project.  The code can easily be adapted to other RPi NeoPixel projects.
