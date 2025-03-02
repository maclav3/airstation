# MicroPython: https://docs.micropython.org/en/latest/
#
# Brandon Gant
# Created: 2019-02-08
# Updated: 2021-11-09
#
# Maciej Bratek
# Adapted for my use case: 2025-01-25
# added install_requirements() function which installs requirements from mip-requirements.txt with mip
# added buzzer notifications for boot start, boot success and boot failure
#
# Source: https://github.com/micropython/micropython/tree/master/ports/esp32#configuring-the-wifi-and-using-the-board
# Source: https://boneskull.com/micropython-on-esp32-part-1/
# Source: https://docs.micropython.org/en/latest/library/network.WLAN.html
#
# Files required to run this script:
#     boot.py
#     key_store.py
#
# Optional files:
#     detect_filesystem.py
#
# Usage:
#     $ pip3 install --user mpfshell
#     $ mpfshell
#     mpfs [/]> open ttyUSB0
#     mpfs [/]> put boot_with_wifi.py boot.py
#     mpfs [/]> put key_store.py
#     mpfs [/]> put detect_filesystem.py
#     mpfs [/]> repl
#     >>>  <Ctrl+] to exit repl>
#
# --OR--
#
#     $ ampy --port /dev/ttyUSB0 put boot_with_wifi.py boot.py
#     $ screen /dev/ttyUSB0 115200
#     >>>  <Ctrl+a then Shift+k to exit repl>
#
# --OR--
#
#    Use the micropython plugin in PyCharm ;)

import utime
import mip
from machine import reset, WDT
from sys import exit
import key_store
from tone import Melody, Note, tones
from tree import print_tree

# Create exceptions (feedback) in cases where normal RAM allocation fails (e.g. interrupts)
from micropython import alloc_emergency_exception_buf


print()
print("=" * 45)
print("boot.py: Press CTRL+C to enter REPL...")
print()

utime.sleep(2)  # A chance to hit Ctrl+C in REPL
alloc_emergency_exception_buf(100)
wdt = WDT(
    timeout=300000
)  # 5-minutes for boot.py to finish and move to main.py / wdt.feed() to reset timer


# Connect to WiFI
def wlan_connect(ssid, password):
    import network
    from ubinascii import hexlify

    wlan = network.WLAN(network.STA_IF)
    if not wlan.active() or not wlan.isconnected():
        wlan.active(True)
        print("       MAC: ", hexlify(wlan.config("mac"), ":").decode())
        print(" WiFi SSID: ", ssid)
        wlan.connect(ssid, password)
        start_wifi = utime.ticks_ms()
        while not wlan.isconnected():
            if (
                utime.ticks_diff(utime.ticks_ms(), start_wifi) > 20000
            ):  # 20 second timeout
                print(f"Wifi Timeout, status: {wlan.status()}... Resetting Device")
                utime.sleep(2)
                reset()
    print("        IP: ", wlan.ifconfig()[0])
    print("    Subnet: ", wlan.ifconfig()[1])
    print("   Gateway: ", wlan.ifconfig()[2])
    print("       DNS: ", wlan.ifconfig()[3])
    print()


# Set RTC using NTP
def ntp():
    import ntptime

    ntptime.host = key_store.get("ntp_host")
    print("NTP Server: ", ntptime.host)
    start_ntp = utime.ticks_ms()
    while (
        utime.time() < 10000
    ):  # Clock is not set with NTP if unixtime is less than 10000
        ntptime.settime()
        if utime.ticks_diff(utime.ticks_ms(), start_ntp) > 10000:  # 10 second timeout
            print("NTP Timeout... Resetting Device")
            reset()
    print(
        "  UTC Time:  {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*utime.localtime())
    )
    print()


# Suppress ESP debug messages in the REPL
def no_debug():
    from esp import osdebug

    osdebug(None)


def mem_stats():
    from esp import flash_size
    from uos import statvfs
    import gc

    fs_stat = statvfs("/")
    fs_size = fs_stat[0] * fs_stat[2]
    fs_free = fs_stat[0] * fs_stat[3]
    fs_used = fs_stat[0] * (fs_stat[2] - fs_stat[3])
    print("Memory Information:")
    print(
        "   RAM Size     {:5,}KB".format(int((gc.mem_alloc() + gc.mem_free()) / 1024))
    )
    print()
    print("Flash Storage Information:")
    print("   Flash Size   {:5,}KB".format(int(flash_size() / 1024)))
    print("   User Space   {:5,}KB".format(int(fs_size / 1024)))
    print("   Free Space   {:5,}KB".format(int(fs_free / 1024)))
    print("   Used Space   {:5,}KB".format(int(fs_used / 1024)))


def filesystem():
    try:
        from boot import check

        print("   File System ", check())
    except ImportError:
        print("detect_filesystem.py module is not present")
        pass


def install_requirements():
    print()
    print("Installing requirements from mip-requirements.txt...")
    print()
    try:
        with open("mip-requirements.txt") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                if line.strip() == "":
                    continue

                try:
                    print(f"\t{line}")
                    mip.install(line)
                except Exception as _err:
                    print(f"\tFailed to install {line}: {_err}")
            print("done.")
    except OSError:
        print("mip-requirements.txt file not found")


_melody_boot_start = Melody(
    Note(tones["C5"], 0.2), Note(tones["E5"], 0.2), Note(tones["G5"], 0.2)
)

_melody_boot_success = Melody(
    Note(tones["G5"], 0.2), Note(tones["E5"], 0.2), Note(tones["C5"], 0.2)
)

_melody_boot_failure = Melody(
    Note(tones["C5"], 0.2), Note(tones["FS5"], 0.2), Note(tones["C5"], 0.2)
)

# Run selected functions at boot
try:
    _melody_boot_start.play()

    no_debug()
    ssid_name = key_store.get("ssid_name")
    ssid_pass = key_store.get("ssid_pass")

    wlan_connect(ssid_name, ssid_pass)
    ntp()  # Only needed if using HTTPS or local timestamp data logging
    # mem_stats()
    # filesystem()  # Detect FAT or littlefs filesystem
    install_requirements()
    # print_tree("/")

    _melody_boot_success.play()
    # TODO: this can be removed when the loop function in main.py is implemented
    # It will feed the timer then, for now – to avoid the irritating watchdog reset – bump the timer to 1 day
    wdt = WDT(
        timeout=86400000
    )  # Watchdog Timer cannot be disabled, so set to expire in 1 day

except KeyboardInterrupt:
    wdt = WDT(
        timeout=86400000
    )  # Watchdog Timer cannot be disabled, so set to expire in 1 day
    exit()
except Exception as err:
    _melody_boot_failure.play()
    print(f"ERROR: {err}\nResetting Device in 30 seconds")
    utime.sleep(30)  # A chance to hit Ctrl+C in REPL
    reset()

wdt.feed()
print("boot.py: end of script")
print("=" * 45)
print()
