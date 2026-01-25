import json
import time

from machine import SoftI2C, Pin
from api_sensordata import SensorStation, get_sensor_community_data
from interrupt import wait_for_interrupt

from lib.lib_lcd1602_2004_with_i2c import LCD
from show_time import show_time


def cycle_stations(lcd:LCD):
    with open("../config.json") as f:
        _conf = json.load(f)

    for _entry in _conf["stations"]:
        station = SensorStation(_entry["name"], _entry["id"], _entry["type"])
        if station.type == "sensor.community":
            lcd.clear()
            lcd.puts(station.name, y=0)
            lcd.puts("Loading...", y=1)

            data = get_sensor_community_data(station)
            print(data)
            to_lcd = data.to_lcd()

            lcd.clear()
            lcd.puts(to_lcd[0], y=0)
            lcd.puts(to_lcd[1], y=1)
            time.sleep(10)


if __name__ == "__main__":
    i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
    lcd = LCD(i2c)

    while True:
        show_time(lcd)
        time.sleep(5)

        cycle_stations(lcd)

        lcd.clear()
        wait_for_interrupt()

# TODO:
# deep sleep with wake on button
# steer LCD brightness & button brightness