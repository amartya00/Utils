r"""
This is a small to-do utility. Enter your to-do as a 1 line entry.
You can enter a due date and also refresh the due date. The todos
are synced via s3. The sync is manual.
"""

import json
import os
import sys
import boto3
import ctypes
import datetime
import argparse
from operator import itemgetter
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../")
from libs.utils.MiscUtils import MiscUtils
from libs.account.CredsManager import CredsManager
from libs.utils.TimeUtils import TimeUtils, TimeUtilsException
from libs.utils.ToDoItem import TodoItem, TodoException
from libs.utils.ToDoList import TodoList

class Todo:
    root = os.path.join(os.environ["HOME"], ".Todo")
    configFile = os.path.join(root, ".config")

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
	    todos = {"Todos" : TodoList()}
	    todos["Todos"].mergeFromMap(json.loads(open(fileName).read())["Todos"]).backfill()
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
	self.todos["Todos"].merge(Todo.checkAndLoadTodoFile(tempsavename)["Todos"])
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
	self.todos["Todos"].clean()
	return self.writeBack().upload()
	
    def addItem(self, text, duedate):
	self.todos["Todos"].addItem(text, duedate)
	return self

    def updateItem(self, todoId, dueDate = None, status = None):
	self.todos["Todos"].updateItem(todoId, dueDate, status)
	return self
	    
    def deleteItem(self, todoId):
	self.todos["Todos"].deleteItem(todoId)
	return self
    
    def getItem(self, todoId):
	if todoId not in self.todos["Todos"].keys():
	    raise TodoException("Item with id: " + todoId + " does not exist")
	else:
	    return self.todos["Todos"][todoId]
	
    def writeBack(self):
	open(os.path.join(Todo.root, self.conf["Key"]), "w").write(json.dumps({"Todos" : self.todos["Todos"].toMap()}, indent = 4))
	return self

    def display(self, sortKey = "DueDate"):
	try:
	    from tabulate import tabulate
	    table = self.todos["Todos"].toLists(sortKey)
	    headers = table[0]
	    values = table[1:]
	    index = headers.index("Status")
	    for i in range(0, len(values)):
		if values[i][index].lower() in ["complete", "done", "finished"]:
		    for j in range(0, len(values[i])):
			values[i][j] = "[*] " + values[i][j]
		elif values[i][index].lower() in ["canceled"]:
		    for j in range(0, len(values[i])):
			values[i][j] = "[x] " + values[i][j]
		else:
		    for j in range(0, len(values[i])):
			values[i][j] = "[ ] " + values[i][j]
	    return "\n\nTodo items:\n--------------------------\n" + tabulate(table[1:], headers = table[0], tablefmt = "pipe") + "\n\n"
	except ImportError as e1:
	    MiscUtils.warn("Type 'sudo pip install tabulate' for prettier output...\n")
	    return "\n\nTodo items:\n--------------------------\n" + json.dumps(self.todos["Todos"], indent = 4) + "\n\n"
	except Exception as e2:
	    raise TodoException(str(e2))

    @staticmethod
    def getOpts(cmdLineArgs):
	parser = argparse.ArgumentParser(prog = "Todo", description = __doc__, usage = "Todo [options]", formatter_class = argparse.RawTextHelpFormatter)
	parser.add_argument("-n", "--newTodo", help = "Text for the new todo. This has to be followed by a -d option.")
	parser.add_argument("-d", "--dueDate", help = "Due date for the item.")
	parser.add_argument("-t", "--status", help = "Status for the item.")
	parser.add_argument("-i", "--todoId", help = "Id of a to-do item.")
	parser.add_argument("-k", "--sortKey", help = "Sortkey to use when viewing the list.")
	parser.add_argument("-u", "--update", help = "Update due date or status for a to do item. This has to be followed by the -i option and the -d / -t option.", action = "store_true")
	parser.add_argument("-x", "--delete", help = "Delete a to do item. This has to be followed by the -i option.", action = "store_true")
	parser.add_argument("-s", "--sync", help = "Downloads the save from S3 and merges it.", action = "store_true")
	parser.add_argument("-c", "--clean", help = "Cleans the completed items in list.", action = "store_true")
	
	args = parser.parse_args(cmdLineArgs)

	dueDate = None
	todoId = None
	status = None
	sortKey = "DueDate"
	
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
	if args.sortKey:
	    sortKey = args.sortKey
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
	    print(t.display(sortKey))
	except TodoException as e:
	    MiscUtils.error(str(e))
	    return False
	return True
	    

		
	
	
	    
