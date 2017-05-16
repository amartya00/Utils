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

class CredsManagerException (Exception):
    def __init__(self, message = "Unknown exception"):
	self.message = message
	
    def __str__(self):
	return self.message

class CredsManager:
    DEFAULT = "DEFAULT"
    CUSTOM = "CUSTOM"
    root = os.path.join(os.environ["HOME"], ".CredsManager")

    @staticmethod
    def checkAndLoadCreds(credsFile, creds):
	if not os.path.exists(CredsManager.root):
	    MiscUtils.info("Creds manager is not configured. Creating folder: " + CredsManager.root)
	    os.makedirs(CredsManager.root)
	    MiscUtils.info("Creating creds file: " + credsFile)
	    open(credsFile, "w").write(json.dumps(creds, indent = 4))
	    return creds
	else:
	    return json.loads(open(credsFile, "r").read())

    @staticmethod
    def getSession(credsFile, mode):
	session = boto3.session.Session()
	if mode == CredsManager.DEFAULT:
	    creds = botocore.session.get_session().get_credentials()
	    setattr(session, "aws_access_key", creds.access_key)
	    setattr(session, "aws_secret_key", creds.secret_key)
	    if hasattr(creds, "aws_session_token"):
		setattr(session, "aws_session_token", creds.session_token)
	    return session
	else:
	    creds = json.loads(open(credsFile, "r").read())
	    setattr(session, "aws_access_key", creds["AccessKey"])
	    setattr(session, "aws_secret_key", creds["SecretKey"])
	    if "SessionToken" in creds.keys() and not creds["SessionToken"] == None:
		setattr(session, "aws_session_token", creds["SessionToken"])
	    MiscUtils.debug("Returning session with access key: " + session.aws_access_key)
	    MiscUtils.debug("Returning session with secret key: " + session.aws_secret_key)
	    return session
	
    def __init__(self):
	self.conf = {
	    "Creds": {
		"Mode" : CredsManager.DEFAULT,
		"AccessKey" : None,
		"SecretKey" : None,
		"SessionToken" : None,
		"Region" : "us-east-1"
	    },
	    "CredsFile" : os.path.join(CredsManager.root, ".credentials")
	}
	self.conf["Creds"] = CredsManager.checkAndLoadCreds(self.conf["CredsFile"], self.conf["Creds"])
	self.conf["Session"] = CredsManager.getSession(self.conf["CredsFile"], self.conf["Creds"]["Mode"]) 
	

    def configure(self):
	promptAccessKey = " [] " if self.conf["Creds"]["AccessKey"] == None else (" [" + self.conf["Creds"]["AccessKey"][0:3] + "***] ")
	promptSecretKey = " [] " if self.conf["Creds"]["SecretKey"] == None else (" [" + self.conf["Creds"]["SecretKey"][0:3] + "***] ")
	promptSessionToken = " [] " if self.conf["Creds"]["SessionToken"] == None else (" [" + self.conf["Creds"]["SessionToken"][0:3] + "***] ")
	promptRegion = " [] " if self.conf["Creds"]["Region"] == None else (" [" + self.conf["Creds"]["Region"] + "] ")
	
	print("Enter AWS access key " +  promptAccessKey + " : ")
	accessKey = sys.stdin.readline().strip()
	print("Enter AWS secret key " + promptSecretKey + " : ")
	secretKey = sys.stdin.readline().strip()
	print("Enter AWS session token " +  promptSessionToken + " : ")
	sessionToken = sys.stdin.readline().strip()
	print("Enter AWS region " + promptRegion + " : ")
	region = sys.stdin.readline().strip()
	
	if not accessKey == "":
	    self.conf["Creds"]["AccessKey"] = accessKey
	if not secretKey == "":
	    self.conf["Creds"]["SecretKey"] = secretKey
	if not sessionToken == "":
	    self.conf["Creds"]["SessionToken"] = sessionToken
	if not region == "":
	    self.conf["Creds"]["Region"] = region
	return self

    def setMode(self, mode):
	if mode == CredsManager.DEFAULT:
	    self.conf["Creds"]["Mode"] = CredsManager.DEFAULT
	else:
	    self.conf["Creds"]["Mode"] = CredsManager.CUSTOM
	return self

    def writeBack(self):
	open(self.conf["CredsFile"], "w").write(json.dumps(self.conf["Creds"], indent = 4))
	return self
    
    def getResource(self, resourceType):
	session = self.conf["Session"]
	resource = session.resource(resourceType)
	if hasattr(session, "aws_session_token"):
	    return session.resource(
		resourceType,
		aws_access_key_id = session.aws_access_key,
		aws_secret_access_key = session.aws_secret_key,
		aws_session_token = session.aws_session_token)
	else:
	    return session.resource(
		resourceType,
		aws_access_key_id = session.aws_access_key,
		aws_secret_access_key = session.aws_secret_key)

    def show(self):
	return json.dumps(self.conf["Creds"], indent = 4)


    @staticmethod
    def getOpts(cmdLineArgs):
	parser = argparse.ArgumentParser(prog = "CredsManager", description = __doc__, usage = "CredsManager [options]", formatter_class = argparse.RawTextHelpFormatter)
	parser.add_argument("-c", "--configure", help = "Input credentials.", action = "store_true")
	parser.add_argument("-m", "--setMode", help = "Set creds mode (default aws creds vs your own creds).")
	parser.add_argument("-s", "--show", help = "Show the custom creds that might be used.", action = "store_true")
	args = parser.parse_args(cmdLineArgs)

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
	return False

