r"""
This utility has some time related utilities.
"""

import datetime

usentp = False
try:
    import ntplib

    usentp = True
except:
    pass
import pytz
import argparse
from pytz.exceptions import UnknownTimeZoneError


class TimeUtilsException(Exception):
    def __init__(self, message="Unknown exception"):
        self.message = message

    def __str__(self):
        return self.message


class TimeUtils:
    validformats = ["%Y-%m-%d-%H-%M", "%Y-%m-%d-%H", "%Y-%m-%d", "%H:%M"]
    validRelativeTimes = ["now", "today", "tomorrow"]

    @staticmethod
    def getDate(datestr, slow=True):
        if usentp and slow:
            now = datetime.datetime.fromtimestamp(ntplib.NTPClient().request('europe.pool.ntp.org', version=3).tx_time)
        else:
            now = datetime.datetime.now()
        if datestr.lower() == "today":
            return now.replace(hour=23, minute=59)
        if datestr.lower() == "tomorrow":
            return now.replace(hour=23, minute=59) + datetime.timedelta(days=1)
        if datestr.lower() == "now":
            return now
        retval = None
        for f in TimeUtils.validformats:
            try:
                retval = datetime.datetime.strptime(datestr, f)
            except ValueError:
                pass
            if not retval == None:
                if f == "%H:%M":
                    temp = datetime.datetime.now()
                    retval = temp.replace(hour=retval.hour, minute=retval.minute)
                return retval
        raise TimeUtilsException(
            "Invalid time format: " + datestr + ". Allowed formats are: " + str(TimeUtils.validformats) + " and " + str(
                TimeUtils.validRelativeTimes))

    def __init__(self, timestr, timezone):
        self.datetime = TimeUtils.getDate(timestr)
        try:
            self.timezone = None if timezone == None else pytz.timezone(timezone)
        except UnknownTimeZoneError as e:
            raise TimeUtilsException(str(e))
        self.localized = self.datetime if timezone == None else self.timezone.localize(self.datetime)

    def getDateStr(self, fmt):
        try:
            return self.localized.strftime(fmt)
        except ValueError as e:
            raise TimeUtilsException(str(e))

    def getDateTime(self):
        return self.datetime

    @staticmethod
    def getOpts(cmdLineArgs):
        parser = argparse.ArgumentParser(prog="TimeUtils", description=__doc__, usage="Time [options]",
                                         formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-t", "--inputTime", help="Input time.")
        parser.add_argument("-f", "--fmt", help="Display format.")
        args = parser.parse_args(cmdLineArgs)

        tz = None
        fmt = "%Y-%m-%d-%H-%M"
        inputTime = "now"
        if args.inputTime:
            inputTime = args.inputTime
        if args.fmt:
            fmt = args.fmt

        try:
            tu = TimeUtils(inputTime, tz)
            print(tu.getDateStr(fmt))
        except TimeUtilsException as e:
            print(str(e))
            return False
