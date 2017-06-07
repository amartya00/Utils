r"""
This utility allows the user to manage one's own creds.
If left empty, the user can revert to the default aws creds.
Using this, you can save aws key and secret key for latere use.
"""

import sys
import os
import json
import botocore.session
import boto3
import argparse

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../")
from libs.utils.MiscUtils import MiscUtils
from libs.account.Creds import Creds, CredsException
from libs.account.CredsCollection import CredsCollection

class CredsManager:
    root = os.path.join(os.environ["HOME"], ".CredsManager")
    filename = os.path.join(root, ".credentials")
    
    @staticmethod
    def checkAndLoadCreds(credsFile, creds):
	if not os.path.exists(CredsManager.root):
	    MiscUtils.info("Creds manager is not configured. Creating folder: " + CredsManager.root)
	    os.makedirs(CredsManager.root)
	if not os.path.exists(credsFile):
	    MiscUtils.info("Creating creds file: " + credsFile)
	    open(credsFile, "w").write(json.dumps(creds.toJson(), indent = 4))
	    return creds
	else:
	    retval = CredsCollection()
	    return retval.mergeFromJson(json.loads(open(credsFile, "r").read()))
	
    def __init__(self):
	self.conf = {
	    "CredsFile" : os.path.join(CredsManager.root, ".credentials"),
	    "Creds" : CredsCollection()
	}
	self.conf["Creds"] = CredsManager.checkAndLoadCreds(self.conf["CredsFile"], self.conf["Creds"])

    def configure(self):
	promptProfileName = " [DEFAULT] "
	print("Enter profileName: " + promptProfileName)
	profileName = sys.stdin.readline().strip()
	if profileName == "":
	    profileName = "DEFAULT"
	profile = self.conf["Creds"].data[profileName] if profileName in self.conf["Creds"].data.keys() else Creds(profileName, "CUSTOM")
	profile.data["Name"] = profileName

	promptAccessKey    = " [] " if profile.data["AccessKey"]    == None else (" [" + profile.data["AccessKey"][0:3] + "***] ")
	promptSecretKey    = " [] " if profile.data["SecretKey"]    == None else (" [" + profile.data["SecretKey"][0:3] + "***] ")
	promptSessionToken = " [] " if profile.data["SessionToken"] == None else (" [" + profile.data["SessionToken"][0:3] + "***] ")
	promptRegion       = " [] " if profile.data["Region"]       == None else (" [" + profile.data["Region"] + "] ")
	promptMode         = " [] " if profile.data["Mode"]         == None else (" [" + profile.data["Mode"] + "] ")
	
	print("Enter AWS access key " +  promptAccessKey + " : ")
	accessKey = sys.stdin.readline().strip()
	print("Enter AWS secret key " + promptSecretKey + " : ")
	secretKey = sys.stdin.readline().strip()
	print("Enter AWS session token " +  promptSessionToken + " : ")
	sessionToken = sys.stdin.readline().strip()
	print("Enter AWS region " + promptRegion + " : ")
	region = sys.stdin.readline().strip()
	print("Enter mode " + promptMode + " : ")
	mode = sys.stdin.readline().strip()
	
	if not accessKey == "":
	    profile.data["AccessKey"] = accessKey
	if not secretKey == "":
	    profile.data["SecretKey"] = secretKey
	if not sessionToken == "":
	    profile.data["SessionToken"] = sessionToken
	if not region == "":
	    profile.data["Region"] = region
	if not mode == "":
	    profile.data["Mode"] = mode
	self.conf["Creds"].addCreds(profile)
	
	return self

    def writeBack(self):
	open(self.conf["CredsFile"], "w").write(json.dumps(self.conf["Creds"].toJson(), indent = 4))
	return self
    
    def getResource(self, resourceType, profileName = "DEFAULT"):
	if profileName not in self.conf["Creds"].data.keys():
	    raise CredsException("Profile with name '" + profileName + "' not found.")
	else:
	    return self.conf["Creds"].data[profileName].getResource(resourceType)

    def show(self):
	return json.dumps(self.conf["Creds"].toJson(), indent = 4)

    def delete(self, profileName):
	self.conf["Creds"].removeCreds(profileName)
	return self

    @staticmethod
    def getOpts(cmdLineArgs):
	parser = argparse.ArgumentParser(prog = "CredsManager", description = __doc__, usage = "CredsManager [options]", formatter_class = argparse.RawTextHelpFormatter)
	parser.add_argument("-c", "--configure", help = "Input credentials.", action = "store_true")
	parser.add_argument("-m", "--setMode", help = "Set creds mode (default aws creds vs your own creds).")
	parser.add_argument("-s", "--show", help = "Show the custom creds that might be used.", action = "store_true")
	parser.add_argument("-d", "--delete", help = "Delete a profile.")
	args = parser.parse_args(cmdLineArgs)

	try:
	    if args.delete:
		c = CredsManager()
		c.delete(args.delete).writeBack()
		return True
	
	    if args.configure:
		c = CredsManager()
		c.configure().writeBack()
		return True

	    if args.setMode:
		c = CredsManager()
		c.setMode(args.setMode).writeBack()
		return True

	    if args.show:
		c = CredsManager()
		print(c.show())
		return True
	
	    parser.print_help()
	except CredsException as e:
	    MiscUtils.error(str(e))
	    return False
	return True

