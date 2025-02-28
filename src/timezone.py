# Brandon Gant
# Created: 2021-10-13
# Updated: 2021-11-09
#
# Sources:
#   Peter Hinch: https://forum.micropython.org/viewtopic.php?t=3675#p28989
#   https://www.timeanddate.com/time/zones/cst
#
# This script only really works if you have set the time over WiFi using NTP.
# Timezones in North America switch to Daylight Savings Time at 2AM on the Second Sunday in March.
# They switch to Standard Time at 2AM on the First Sunday in November.
#
# Usage:
#   import time
#   from timezone import tz, isDST
#   time.localtime(tz())           # Convert UTC now to CDT/CST
#   time.localtime(tz(679791859))  # Convert UTC timestamp to CDT/CST
#   isDST()                        # Is UTC now Daylight Savings Time?
#   isDST(679791859)               # Is UTC timestamp Daylight Savings Time?
#

import time

UTC_Offset_ST = -6  # CST
UTC_Offset_DST = -5  # CDT


def tz(debug_time=None, format="time"):
    if debug_time is not None:
        t = debug_time  # UTC Unix Timestamp for testing
    else:
        t = time.time()
    year = time.localtime(t)[0]
    start = time.mktime(
        (year, 3, (14 - (int(5 * year / 4 + 1)) % 7), 2, 0, 0, 0, 0)
    )  # 2AM the Second Sunday in March
    end = time.mktime(
        (year, 11, (7 - (int(5 * year / 4 + 1)) % 7), 2, 0, 0, 0, 0)
    )  # 2AM the  First Sunday in November
    if format == "time":
        return (
            t + (3600 * UTC_Offset_ST)
            if t < start or t > end
            else t + (3600 * UTC_Offset_DST)
        )
    elif format == "bool":
        return False if t < start or t > end else True
    else:
        return None


def isDST(t=None):
    return tz(debug_time=t, format="bool")
