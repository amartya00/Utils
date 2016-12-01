r"""
This contains some EC2 related utilities
"""

import boto3
import os
import argparse
from botocore.exceptions import ClientError

class EC2UtilsException (Exception):
    def __init__(self, message = "Unknown Exception"):
	self.message = message

    def __str__(self):
	return self.message
	
class EC2Utils:
    @staticmethod
    def getStdout(instanceId, region, outputDir):
	print("Getting user data stdout for instance " + instanceId)
	try:
	    response = boto3.client("ec2", region_name = region).get_console_output(DryRun = False, InstanceId = instanceId)
	except ClientError as e:
	    raise EC2UtilsException("ERROR: In getStdout for EC2 instance: " + e.response["Error"]["Code"])
	if outputDir != None:
	    outfile = os.path.join(outputDir, instanceId + ".log")
	else:
	    outfile = instanceId + ".log"
	open(outfile, "w").write(response["Output"])
	print("Saved user data in file: " + outfile)
	return True

    @staticmethod
    def getOpts(cmdLineArgs):
	parser = argparse.ArgumentParser(prog = "EC2Utils", description = __doc__, usage = "RunTemplate -t <templateFile> [-p <paramFile>] [-o <cmdLineOverrides>] [-d <outputDir>]", formatter_class = argparse.RawTextHelpFormatter)
	parser.add_argument("-i", "--instanceId", help = "The instance ID")
	parser.add_argument("-r", "--region", help = "The region")
	parser.add_argument("-d", "--outputDir", help = "The log output directory (default is pwd)")
	
	args = parser.parse_args(cmdLineArgs)

	region = None
	instanceId = None
	outputDir = None

	if args.region:
	      region = args.region

	if args.instanceId:
	      instanceId = args.instanceId

	if args.outputDir:
	      outputDir = args.outputDir


	if instanceId == None or region == None:
	      print("ERROR: InstanceId and region is needed")
	      parser.print_help()
	      return False
	try:
	    EC2Utils.getStdout(instanceId, region, outputDir)
	except EC2UtilsException as e:
	    print(str(e))
	    return False
	
		
