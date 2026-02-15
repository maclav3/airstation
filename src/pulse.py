import math
import uasyncio as asyncio

from machine import PWM

sine = [(math.sin(i / 50 * 2 * math.pi) + 1) / 2 for i in range(200)]

async def pulse_task(button_highlight_pin: PWM):
    print("Starting LED pulse...")
    while True:
        for i in range(50):
            button_highlight_pin.duty_u16(int(sine[i] * 65535))
            await asyncio.sleep_ms(40)