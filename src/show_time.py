import time

from lib.lib_lcd1602_2004_with_i2c import LCD


def show_time(lcd: LCD):
    lcd.clear()
    now = time.localtime()
    d = "{:04d}/{:02d}/{:02d}".format(now[0], now[1], now[2])
    lcd.puts(d, y=0)
    t = "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])
    lcd.puts(t, y=1)
