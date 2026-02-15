from machine import Pin
import time

button = Pin(4, Pin.IN, Pin.PULL_UP)

# Flag set in IRQ, processed in main loop
irq_flag = False


def irq_handler(pin):
    global irq_flag
    irq_flag = True  # minimal work in IRQ


# Configure IRQ for falling edge (press -> low)
button.irq(trigger=Pin.IRQ_FALLING, handler=irq_handler)


def wait_for_interrupt():
    # Main loop processes the event and debounces
    global irq_flag

    while True:
        if irq_flag:
            irq_flag = False
            # simple debounce
            time.sleep_ms(50)
            if button.value() == 0:
                # button pressed, return
                return
        # other background tasks
        time.sleep_ms(10)
