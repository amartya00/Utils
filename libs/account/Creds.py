r"""
This forms the creds class.
"""

import boto3
import botocore.session


class CredsException(Exception):
    def __init__(self, message="Unknown exception"):
        self.message = message

    def __str__(self):
        return self.message


class Creds:
    DEFAULT = "DEFAULT"
    CUSTOM = "CUSTOM"
    allowedModes = [DEFAULT, CUSTOM]

    def __init__(self, profileName="DEFAULT", mode=DEFAULT):
        if mode not in [Creds.DEFAULT, Creds.CUSTOM]:
            raise CredsException("Mode cannot be '" + mode + "'. Allowed values: " + str(Creds.allowedModes))
        self.data = {
            "Name": profileName,
            "Mode": mode,
            "AccessKey": None,
            "SecretKey": None,
            "SessionToken": None,
            "Region": None
        }
        if self.data["Mode"] == Creds.DEFAULT:
            creds = botocore.session.get_session().get_credentials()
            self.data["AccessKey"] = creds.access_key
            self.data["SecretKey"] = creds.secret_key
            if hasattr(creds, "aws_session_token"):
                self.data["SessionToken"] = creds.session_token

    def mergeFromOther(self, other):
        if self.data["AccessKey"] == None:
            self.data["AccessKey"] = other.data["AccessKey"]
        if self.data["SecretKey"] == None:
            self.data["SecretKey"] = other.data["SecretKey"]
        if self.data["SessionToken"] == None:
            self.data["SessionToken"] = other.data["SessionToken"]
        if self.data["Region"] == None:
            self.data["Region"] = other.data["Region"]
        if self.data["Mode"] == None:
            self.data["Mode"] = other.data["Mode"]
        return self

    def mergeFromJson(self, other):
        if self.data["AccessKey"] == None:
            self.data["AccessKey"] = other["AccessKey"]
        if self.data["SecretKey"] == None:
            self.data["SecretKey"] = other["SecretKey"]
        if self.data["SessionToken"] == None:
            self.data["SessionToken"] = other["SessionToken"]
        if self.data["Region"] == None:
            self.data["Region"] = other["Region"]
        if self.data["Mode"] == None:
            self.data["Mode"] = other["Mode"]
        return self

    def updateFromOther(self, other):
        if not other.data["AccessKey"] == None:
            self.data["AccessKey"] = other.data["AccessKey"]
        if not other.data["SecretKey"] == None:
            self.data["SecretKey"] = other.data["SecretKey"]
        if not other.data["SessionToken"] == None:
            self.data["SessionToken"] = other.data["SessionToken"]
        if not other.data["Region"] == None:
            self.data["Region"] = other.data["Region"]
        if not other.data["Mode"] == None:
            self.data["Mode"] = other.data["Mode"]
        return self

    def updateFromJson(self, other):
        if not other["AccessKey"] == None:
            self.data["AccessKey"] = other["AccessKey"]
        if not other["SecretKey"] == None:
            self.data["SecretKey"] = other["SecretKey"]
        if not other["SessionToken"] == None:
            self.data["SessionToken"] = other["SessionToken"]
        if not other["Region"] == None:
            self.data["Region"] = other["Region"]
        if not other["Mode"] == None:
            self.data["Mode"] = other["Mode"]
        return self

    def getSession(self):
        session = boto3.session.Session()
        creds = botocore.session.get_session().get_credentials()
        setattr(session, "aws_access_key", self.data["AccessKey"])
        setattr(session, "aws_secret_key", self.data["SecretKey"])
        if not self.data["SessionToken"] == None:
            setattr(session, "aws_session_token", self.data["SessionToken"])
        return session

    def getResource(self, resourceType):
        session = self.getSession()
        resource = session.resource(resourceType)
        if hasattr(session, "aws_session_token"):
            return session.resource(
                resourceType,
                aws_access_key_id=session.aws_access_key,
                aws_secret_access_key=session.aws_secret_key,
                aws_session_token=session.aws_session_token)
        else:
            return session.resource(
                resourceType,
                aws_access_key_id=session.aws_access_key,
                aws_secret_access_key=session.aws_secret_key)
