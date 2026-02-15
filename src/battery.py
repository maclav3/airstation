import time

from machine import Pin, PWM, ADC

# LED indicator to light up when the battery is low or critical
_battery_low = PWM(Pin(15, Pin.OUT))
_battery_low.freq(1000)

_battery_adc = ADC(Pin(34, Pin.IN), atten=ADC.ATTN_11DB)


def _get_battery_voltage() -> float:
    # Take multiple samples to smooth out noise
    measurements = []
    for _ in range(20):
        measurements.append(_battery_adc.read_u16())
        time.sleep_ms(2)

    # 4.10 V = 36888
    avg = sum(measurements) / len(measurements)
    voltage = avg * 4.10 / 36888

    return voltage


def check_battery() -> tuple[float, float]:
    voltage = _get_battery_voltage()
    if voltage == 0:
        return voltage, 0
    percentage = (voltage - 3.2) / (4.2 - 3.2) * 100

    return voltage, percentage


def toggle_battery_light(on: bool, bright: bool = False):
    duty = int(65535 / 2) if bright else int(65535 / 5)
    duty = duty if on else 0

    _battery_low.duty_u16(duty)
