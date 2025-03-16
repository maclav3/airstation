import glob
import os
import sys


def choose_device() -> str:
    env = os.getenv("USB_PORT")
    if env:
        return env

    usb_devices = glob.glob("/dev/ttyUSB*")
    if not usb_devices:
        raise Exception("No USB devices found")

    if len(usb_devices) == 1:
        return usb_devices[0]

    s = "Multiple USB devices found:\n"
    for i, device in enumerate(usb_devices):
        s += f"{i + 1}. {device}\n"

    s += "Use the USB_PORT environment variable to choose one"
    sys.stderr.write(s)
    return ""


if __name__ == "__main__":
    print(choose_device())
