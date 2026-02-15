import json
import time

import uasyncio as asyncio

import battery
import esp32

from machine import SoftI2C, Pin, PWM, deepsleep

import pulse
from api_sensordata import SensorStation, get_sensor_community_data
from lib.lib_lcd1602_2004_with_i2c import LCD

# from show_time import show_time

button_highlight_pin = PWM(Pin(23, Pin.OUT))
button_highlight_pin.freq(1000)
pulse_task = None

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
lcd = LCD(i2c)


async def cycle_stations():
    with open("../config.json") as f:
        _conf = json.load(f)

    for _entry in _conf["stations"]:
        station = SensorStation(_entry["name"], _entry["id"], _entry["type"])
        if station.type == "sensor.community":
            lcd.clear()
            lcd.puts(station.name, y=0)
            lcd.puts("Loading...", y=1)

            data = await get_sensor_community_data(station)
            print(data)
            to_lcd = data.to_lcd()

            lcd.clear()
            lcd.puts(to_lcd[0], y=0)
            lcd.puts(to_lcd[1], y=1)
            await asyncio.sleep(4)


def flash_battery_critical():
    for i in range(20):
        battery.toggle_battery_light(on=True, bright=(i % 2 == 0))
        time.sleep(0.1)
    battery.toggle_battery_light(on=False)


def shutdown():
    print("going to deep sleep")
    lcd.clear()
    lcd.backlight(False)
    battery.toggle_battery_light(False)

    if pulse_task:
        pulse_task.cancel()
    asyncio.sleep_ms(10)

    # The button should connect Pin 4 to GND.
    wake_pin = Pin(4, Pin.IN, Pin.PULL_UP)

    esp32.wake_on_ext0(pin=wake_pin, level=0)
    print("deep sleep!")
    deepsleep()
    exit()


async def show_info():
    # show_time(lcd)
    await cycle_stations()
    shutdown()


if __name__ == "__main__":
    # battery check
    battery.toggle_battery_light(on=False)
    battery_voltage, battery_percentage = battery.check_battery()
    # battery_voltage = 0 probably means that battery is taken out and you're powering the ESP32 from a USB port
    if 0.5 < battery_voltage <= 3.2:
        flash_battery_critical()
        print("Battery critical, going to sleep")
        shutdown()

    lcd.backlight(True)
    lcd.clear()
    if 0.5 < battery_voltage <= 3.4:
        print("Battery low!")
        battery.toggle_battery_light(on=True, bright=False)  # on until shutdown
    if battery_voltage == 0:
        print("Battery off, probably running off USB cable")
    else:
        msg = "Battery: {:3d}%".format(max(int(battery_percentage), 0))
        lcd.puts(msg, y=0)
        print(msg)
        time.sleep(1)

    pulse_task = asyncio.create_task(pulse.pulse_task(button_highlight_pin))
    asyncio.create_task(show_info())
    asyncio.get_event_loop().run_forever()
