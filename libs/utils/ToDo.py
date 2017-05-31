r"""
This is a small to-do utility. Enter your to-do as a 1 line entry.
You can enter a due date and also refresh the due date. The todos
are synced vis s3. The sync is manual.
"""

import json
import os
import sys
import boto3
import ctypes
import datetime
import argparse
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../")
from libs.utils.MiscUtils import MiscUtils
from libs.account.CredsManager import CredsManager
from libs.utils.TimeUtils import TimeUtils, TimeUtilsException

class TodoException (Exception):
    def __init__(self, message = "Unknown exception"):
	self.message = message

    def __str__(self):
	return self.message

class Todo:
    root = os.path.join(os.environ["HOME"], ".Todo")
    configFile = os.path.join(root, ".config")
    validStatus = ["IN_PROGRESS", "CREATED", "COMPLETE", "BLOCKED", "CANCELED"]
    @staticmethod
    def checkAndCreateConfig(content):	
	if not os.path.exists(Todo.root):
	    MiscUtils.info("Creating .Todo folder and .config file as they do not exist")
	    os.makedirs(Todo.root)
	    open(Todo.configFile, "w").write(json.dumps(content, indent = 4))
	    return content
	elif not os.path.isfile(Todo.configFile):
	    MiscUtils.info("Creating .config file as it does not exist")
	    open(Todo.configFile, "w").write(json.dumps(content, indent = 4))
	    return content
	else:
	    MiscUtils.debug("Found root folder and config file")
	    return json.loads(open(Todo.configFile).read())

    @staticmethod
    def checkAndLoadTodoFile(fileName):
	if not os.path.isfile(fileName):
	    open(fileName, "w").write(json.dumps({"Todos" : {}}))
	    return {"Todos" : {}}
	else:
	    todos = json.loads(open(fileName).read())
	    #Backfill status
	    for k in todos["Todos"].keys():
		if "Status" not in todos["Todos"][k]:
		    todos["Todos"][k]["Status"] = "CREATED"
	    return todos
		    
	    
    def __init__(self):
	self.conf = {
	    "User" : os.environ["USER"],
	    "Bucket" : "Todo-" + os.environ["USER"],
	    "Key" : "Todo.json"
	}
	try:
	    self.conf = Todo.checkAndCreateConfig(self.conf)
	except EnvironmentError as e:
	    raise TodoException("Could not create / read config file: " + Todo.configFile + " because: " + str(e))
	self.todos = Todo.checkAndLoadTodoFile(os.path.join(Todo.root, self.conf["Key"]))

    def downloadAndMerge(self):
	credsManager = CredsManager()
	bucket = credsManager.getResource("s3").Bucket(self.conf["Bucket"])
	tempsavename = os.path.join(Todo.root, ".temp.json")
	try:
	    bucket.download_file(self.conf["Key"], tempsavename)
	except ClientError as e:
	    if e.response["Error"]["Code"] == "404":
		raise TodoException("Either bucket (" + self.conf["Bucket"] + ") or key (" + self.conf["Key"] + ") not found. If you never uploaded the todos, ignore this")
	    else:
		raise TodoException(e.response["Error"]["Code"] + " : " + e.response["Error"]["Message"])
	MiscUtils.info("Downloaded from S3. Merging")
	remotetodos = json.loads(open(tempsavename).read())
	for i in remotetodos["Todos"].keys():
	    if not i in self.todos["Todos"].keys():
		if "Status" not in remotetodos["Todos"][i].keys():
		    remotetodos["Todos"][i]["Status"] = "CREATED"
		self.todos["Todos"][i] = remotetodos["Todos"][i]
	    else:
		 MiscUtils.debug("Skipping merging todo: " + remotetodos["Todos"][i]["Description"])
	MiscUtils.info("Merged and saved all to-dos")
	return self

    def upload(self):
	credsManager = CredsManager()
	bucket = credsManager.getResource("s3").Bucket(self.conf["Bucket"])
	try:
	    bucket.upload_file(os.path.join(Todo.root, self.conf["Key"]), self.conf["Key"])
	except ClientError as e:
	    raise TodoException(e.response["Error"]["Code"] + " : " + e.response["Error"]["Message"])
	except S3UploadFailedError as e:
	    raise TodoException(str(e))
	MiscUtils.info("Uploaded " + self.conf["Key"] + " to S3")
	return self

    def sync(self):
	return self.downloadAndMerge().writeBack().upload()

    def clean(self):
	self.downloadAndMerge()
	itemsToDelete = []
	for t in self.todos["Todos"].keys():
	    if ("Status" in  self.todos["Todos"][t].keys()) and  (self.todos["Todos"][t]["Status"].lower() in ["complete", "done", "finished"]):
		itemsToDelete.append(t)
	for i in itemsToDelete:
	    MiscUtils.debug("Deleting: " + self.todos["Todos"][i]["Description"])
	    self.deleteItem(i)
	return self.writeBack().upload()
	
    def addItem(self, text, duedate):
	try:
	    self.todos["Todos"][str(ctypes.c_size_t(hash(text)).value)] = {
		"Description" : text,
		"DueDate" : datetime.datetime.strptime(duedate, TimeUtils.validformats[0]).strftime(TimeUtils.validformats[0]),
		"Status" : "CREATED"
	    }
	except ValueError as e:
	    raise TodoException("Please enter values in correct format: " + str(e))
	return self

    def updateItem(self, todoId, dueDate = None, status = None):
	if not todoId in self.todos["Todos"].keys():
	    raise TodoException("Invalid id: " + todoId)
	else:
	    if not dueDate == None:
		self.todos["Todos"][todoId]["DueDate"] = dueDate
	    if not status == None:
		if status.upper() not in Todo.validStatus:
		    raise TodoException("Invalid todo status: '" + status + "'. valid statuses are: " + str(Todo.validStatus))
		self.todos["Todos"][todoId]["Status"] = status.upper()
	    return self
	    
    def deleteItem(self, todoId):
	if not todoId in self.todos["Todos"].keys():
	    raise TodoException("Invalid id: " + todoId)
	else:
	    del(self.todos["Todos"][todoId])
	return self
    
    def getItem(self, todoId):
	if todoId not in self.todos["Todos"].keys():
	    raise TodoException("Item with id: " + todoId + " does not exist")
	else:
	    return self.todos["Todos"][todoId]
	
    def writeBack(self):
	open(os.path.join(Todo.root, self.conf["Key"]), "w").write(json.dumps(self.todos, indent = 4))
	return self

    def display(self):
	try:
	    from tabulate import tabulate
	    ids = []
	    texts = []
	    dates = []
	    status = []
	    
	    for k in self.todos["Todos"].keys():
		ids.append(k)
		dates.append(self.todos["Todos"][k]["DueDate"])
		if self.todos["Todos"][k]["Status"].lower() in ["complete", "done", "finished"]:
		    status.append("[*] " + self.todos["Todos"][k]["Status"])
		    texts.append("[*] " + self.todos["Todos"][k]["Description"])
		elif self.todos["Todos"][k]["Status"].lower() in ["canceled"]:
		    status.append("[x] " + self.todos["Todos"][k]["Status"])
		    texts.append("[x] " + self.todos["Todos"][k]["Description"])
		else:
		    status.append("[ ] " + self.todos["Todos"][k]["Status"])
		    texts.append("[ ] " + self.todos["Todos"][k]["Description"])
	    return "\n\nTodo items:\n--------------------------\n" + tabulate({
		"ID": ids,
		"Description": texts,
		"Due by" : dates,
		"Status" : status
	    }, headers="keys", tablefmt="pipe") + "\n\n"
	except Exception as e:
	    print("[WARN] type 'sudo pip install tabulate' for prettier output...\n")
	    return "\n\nTodo items:\n--------------------------\n" + json.dumps(self.todos["Todos"], indent = 4) + "\n\n"

    @staticmethod
    def getOpts(cmdLineArgs):
	parser = argparse.ArgumentParser(prog = "Todo", description = __doc__, usage = "Todo [options]", formatter_class = argparse.RawTextHelpFormatter)
	parser.add_argument("-n", "--newTodo", help = "Text for the new todo. This has to be followed by a -d option.")
	parser.add_argument("-d", "--dueDate", help = "Due date for the item.")
	parser.add_argument("-t", "--status", help = "Status for the item.")
	parser.add_argument("-i", "--todoId", help = "Id of a to-do item.")
	parser.add_argument("-u", "--update", help = "Update due date or status for a to do item. This has to be followed by the -i option and the -d / -t option.", action = "store_true")
	parser.add_argument("-x", "--delete", help = "Delete a to do item. This has to be followed by the -i option.", action = "store_true")
	parser.add_argument("-s", "--sync", help = "Downloads the save from S3 and merges it.", action = "store_true")
	parser.add_argument("-c", "--clean", help = "Cleans the completed items in list.", action = "store_true")
	args = parser.parse_args(cmdLineArgs)

	dueDate = None
	todoId = None
	status = None
	
	if args.dueDate:
	    try:
		t = TimeUtils(args.dueDate, None)
		dueDate = t.getDateStr(TimeUtils.validformats[0])
	    except TimeUtilsException  as e:
		MiscUtils.error(str(e))
	if args.todoId:
	    todoId = str(args.todoId)
	if args.status:
	    status = args.status
	# Add
	if args.newTodo:
	    text = args.newTodo
	    if dueDate == None:
		MiscUtils.error("Due date needed for new task")
		return False
	    else:
		try:
		    t = Todo()
		    t.addItem(text, dueDate).writeBack()
		except TodoException as e:
		    MiscUtils.error(str(e))
		    return False
		return True
	# Update
	if args.update:
	    if todoId == None:
		MiscUtils.error("Both todo-id and due date required")
		return False
	    else:
		try:
		    t = Todo()
		    t.updateItem(todoId, dueDate, status).writeBack()
		except TodoException as e:
		    MiscUtils.error(str(e))
		    return False
		return True
	
	# Delete
	if args.delete:
	    if todoId == None:
		MiscUtils.error("Need the item id")
		return False
	    else:
		try:
		    t = Todo()
		    t.deleteItem(todoId).writeBack()
		except TodoException as e:
		    MiscUtils.error(str(e))
		    return False
		return True	
	# Sync
	if args.sync:
	    try:
		t = Todo()
		t.sync().writeBack()
	    except TodoException as e:
		MiscUtils.error(str(e))
		return False
	    return True

	# Clean
        if args.clean:
	    try:
		t = Todo()
		t.clean()
	    except TodoException as e:
		MiscUtils.error(str(e))
		return False
	    return True
	
	#Display
        try:
	    t = Todo()
	    print(t.display())
	except TodoException as e:
	    MiscUtils.error(str(e))
	    return False
	return True
	    

		
	
	
	    
