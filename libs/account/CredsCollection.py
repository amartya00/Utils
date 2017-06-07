r"""
Colloection of profiles
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../")
from libs.account.Creds import Creds, CredsException

class CredsCollection:
    def __init__(self):
	self.data = {
	}

    def addCreds(self, creds):
	self.data[creds.data["Name"]] = creds

    def removeCreds(self, profileName):
	if profileName not in self.data.keys():
	    raise CredsException("No profile found with name '" + profileName + "'.")
	del self.data[profileName]
	return self

    def toJson(self):
	retval = {
	}
	for p in self.data.keys():
	    retval[p] = self.data[p].data
	return retval

    def mergeFromJson(self, data):
	for p in data.keys():
	    if p not in self.data.keys():
		self.data[p] = Creds(data[p]["Name"], data[p]["Mode"])
		self.data[p].mergeFromJson(data[p])
	return self
