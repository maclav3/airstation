import os

from machine import SDCard

_mounted = False

def mount(mount_point: str = '/sd'):
    global _mounted
    if _mounted:
        return

    sd = SDCard(slot=2, freq=40000)
    try:
        os.mount(sd, mount_point)
        _mounted = True
    except Exception as e:
        print("Failed to mount SD card: %s" % e)
        _mounted = False