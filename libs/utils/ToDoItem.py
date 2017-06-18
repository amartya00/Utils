r"""
This is a todo item
"""

import ctypes
import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../")
from libs.utils.TimeUtils import TimeUtils, TimeUtilsException


class TodoException(Exception):
    def __init__(self, message="Unknown exception"):
        self.message = message

    def __str__(self):
        return self.message


class TodoItem:
    validStatus = ["IN_PROGRESS", "CREATED", "COMPLETE", "BLOCKED", "CANCELED"]

    @staticmethod
    def getDefaultItem():
        retval = TodoItem()
        retval.setter(
            {
                "CreateDate": datetime.datetime.now().strftime(TimeUtils.validformats[0]),
                "DueDate": datetime.datetime.now().strftime(TimeUtils.validformats[0]),
                "LastModified": datetime.datetime.now().strftime(TimeUtils.validformats[0]),
                "Status": "CREATED"
            }
        )
        return retval

    def __init__(self):
        self.data = {
            "Description": None,
            "CreateDate": None,
            "DueDate": None,
            "Status": None,
            "LastModified": None,
            "Id": None
        }

    def toList(self):
        return [
            self.data["Description"],
            self.data["CreateDate"],
            self.data["DueDate"],
            self.data["Status"],
            self.data["LastModified"],
            self.data["Id"]
        ]

    def computeId(self):
        if self.data["Description"] == None:
            return None
        else:
            return str(ctypes.c_size_t(hash(self.data["Description"])).value)

    def setter(self, attributes):
        try:
            if "Description" in attributes.keys() and not attributes["Description"] == None:
                self.data["Description"] = attributes["Description"]

            if "Id" in attributes.keys() and not attributes["Id"] == None:
                self.data["Id"] = attributes["Id"]

            if "CreateDate" in attributes.keys() and not attributes["CreateDate"] == None:
                self.data["CreateDate"] = TimeUtils.getDate(attributes["CreateDate"], False).strftime(
                    TimeUtils.validformats[0])

            if "DueDate" in attributes.keys() and not attributes["DueDate"] == None:
                self.data["DueDate"] = TimeUtils.getDate(attributes["DueDate"], False).strftime(
                    TimeUtils.validformats[0])

            if "LastModified" in attributes.keys() and not attributes["LastModified"] == None:
                self.data["LastModified"] = TimeUtils.getDate(attributes["LastModified"], False).strftime(
                    TimeUtils.validformats[0])

            if "Status" in attributes.keys() and not attributes["Status"] == None:
                if attributes["Status"].upper() not in TodoItem.validStatus:
                    raise TodoException(
                        "Invalid todo status: '" + attributes["Status"] + "'. valid statuses are: " + str(
                            TodoItem.validStatus))
                self.data["Status"] = attributes["Status"].upper()
            return self
        except ValueError as e:
            raise TodoException("Please enter values in correct format: " + str(e))
        except TimeUtilsException as e:
            raise TodoException(str(e))

    def backfill(self):
        if self.data["Status"] == None:
            self.data["Status"] = "CREATED"
        if self.data["CreateDate"] == None:
            self.data["CreateDate"] = datetime.datetime.now().strftime(TimeUtils.validformats[0])
        if self.data["DueDate"] == None:
            self.data["DueDate"] = datetime.datetime.now().strftime(TimeUtils.validformats[0])
        if self.data["LastModified"] == None:
            self.data["LastModified"] = datetime.datetime.now().strftime(TimeUtils.validformats[0])
        return self
