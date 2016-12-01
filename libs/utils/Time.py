r"""
A small time utility
"""
import os
import datetime
import pytz
import sys
import argparse
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../")
from libs.utils.MiscUtils import MiscUtils

useNtp = True
try:
	import ntplib
except ImportError:
	useNtp = False
	

class TimeException (Exception):
	def __init__(self, message = "Unknown exception"):
		self.message = message

	def __str__(self):
		return self.message
class Time:
	@staticmethod
	# Date string is in PST of epoch
	# Return always in UTC
	def createDate(dateString): 
		dates = ["mm", "HH", "DD", "MM", "YYYY"]
		temp = dateString.split("-")
		if len(temp) == 1: # Epoch input
			retVal = datetime.datetime.fromtimestamp(float(dateString), tz = pytz.timezone("UTC"))
		else: # PST input
			i = 0
			for t in reversed(temp):
				dates[i] = t
				i = i+1
			retVal = datetime.datetime.now(pytz.timezone("US/Pacific"))
			if dates[0] != "mm":
				retVal = retVal.replace(minute = int(dates[0]))
			if dates[1] != "HH":
				retVal = retVal.replace(hour = int(dates[1]))
			if dates[2] != "DD":
				retVal = retVal.replace(day = int(dates[2]))
			if dates[3] != "MM":
				retVal = retVal.replace(month = int(dates[3]))
			if dates[4] != "YYYY":
				retVal = retVal.replace(year = int(dates[4]))
			retVal = retVal + datetime.timedelta(hours = 7)
			retVal = retVal.replace(tzinfo = pytz.timezone("UTC"))
		return retVal
	
	@staticmethod
	def time(inputTime = None, outFormat = "Default"):
		TZ  = "US/Pacific"
		TZ1 = "UTC"
		if inputTime == None: # Time is now
			MiscUtils.debug(">> Printing current time")
			if useNtp:
				MiscUtils.debug(">> Using NTPLIB")
				timeValUTC = datetime.datetime.utcnow()
				timeValSeattle = datetime.datetime.fromtimestamp(ntplib.NTPClient().request('europe.pool.ntp.org', version=3).tx_time)
			else:
				print("WARN: Printing current time in PST without using ntplib. This will not take into account daylight savings time. The UTC time will still be correct. The PST might be wrong.")
				timeValUTC     = datetime.datetime.utcnow()
				timeValSeattle = timeValUTC - datetime.timedelta(hours = 7)
			return (timeValSeattle.strftime("%Y-%m-%d-%H-%M"), timeValUTC.strftime("%Y-%m-%d-%H-%M"))
		else: # Time = input time
			timeValUTC     = Time.createDate(inputTime)
			timeValSeattle = timeValUTC - datetime.timedelta(hours = 7)
		
		if outFormat == "default": # Display format = YYYY-MM-DD-hh-mm
			return (timeValSeattle.strftime("%Y-%m-%d-%H-%M"), timeValUTC.strftime("%Y-%m-%d-%H-%M"))
		elif outFormat == "epoch": # Display format = epoch
			t1 = str((timeValUTC - datetime.datetime(1970, 1, 1, tzinfo = pytz.timezone(TZ1))).total_seconds())
			return (t1, t1)
		else:
			try:
				return (timeValSeattle.strptime(outFormat), timeValUTC.strptime(outFormat))
			except:
				raise TimeException("Invalid format")

	@staticmethod
	def getOpts(cmdLineArgs):
		parser = argparse.ArgumentParser(prog = "Tasks", description = __doc__, usage = "Time [options]", formatter_class = argparse.RawTextHelpFormatter)
		parser.add_argument("-f", "--format", help = "A strftime compatible format for displaying the time")
		parser.add_argument("-t", "--inputTime", help = "Input time in PST and the format you provided with -f. The output will be the corresponding time in UTC")
    
		args = parser.parse_args(cmdLineArgs)

		PST = None
		UTC = None

		f = None
		t = None

		if args.format:
			f = args.format

		if args.inputTime:
			t = args.inputTime

		try:
			PST, UTC = Time.time(t, f)
			print(PST + " PST")
			print(UTC + " UTC")
			return True
		except TimeException as e:
			MiscUtils.debug("Recieved time exception")
			print(e)
			parser.print_help()
			return 1
		except Exception as e:
			print(e)
			parser.print_help()
			return 1


