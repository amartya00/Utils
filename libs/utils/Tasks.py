#!/usr/bin/env python
r"""
This is a very simple task management utility. You can create,
and  keep track of  tasks,  update  them  and delete them. All 
this does is create a folder with the  taskname  in  ~/.Tasks.  
It  also creates 2 subfolders called  docs and  logs. It  also 
exports some environment  variables: SCRATCH and __TASK__
"""

import json
import os
import argparse
import shutil
import tarfile
import sys
import datetime
import time

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../")
from libs.utils.MiscUtils import MiscUtils

class TasksException(BaseException):
    r"""
    Tasks Exception is used for all exceptions related to tasks
    """
    def __init__(self, message = "Unknown error"):
        self.message = message

    def __str__(self):
        return self.message
    
class Tasks:
    r"""
    Tasks class that encapsulates all functions
    """
    tasksRoot = os.environ["HOME"] + "/.Tasks/"
    archiveRoot = os.environ["HOME"] + "/.TasksArchive/"
    tasksData = tasksRoot + "/.data"
    
    def __init__(self, taskName):
        self.inATask = True if "CURRENT_TASK" in os.environ.keys() else False
        self.taskRoot = Tasks.tasksRoot + "/" + taskName
        self.configFile = self.taskRoot + "/.config"
        self.archiveFile = taskName + ".tar.gz"
	self.taskName = taskName
        if os.path.isfile(self.configFile):
            self.config = json.loads(open(self.configFile, "r").read())
        else:
            self.config = {"NAME" : taskName, "STATUS": "Unknown", "Checklist" : []}

    def createTask(self):
        r"""
        Creates a task
        """
        if os.path.isdir(self.taskRoot):
            raise TasksException("Task already exists") 
        os.makedirs(self.taskRoot + "/docs")
        os.makedirs(self.taskRoot + "/logs")
        self.config["STATUS"] = "Created"
	self.config["CREATE_DATE"] = str(datetime.datetime.now().strftime("%b %d %Y %H:%M")) + " " + time.tzname[0]
        open(self.configFile, "w").write(json.dumps(self.config, indent = 4))
        Tasks.refreshTasksData()
        return self

    def updateTask(self, status):
        r"""
        Updates the status of a task
        """
        self.config["STATUS"] = status
        open(self.configFile, "w").write(json.dumps(self.config, indent = 4))
        Tasks.refreshTasksData()
        return self

    def enterTask(self):
        r"""
        Enters a task. Creates a new shell with lots of handy env variables
        """
        if self.inATask:
            raise TasksException("Already in a task")
	if self.config["NAME"] not in [t["NAME"] for t in Tasks.listTasks()]:
	    raise TasksException("No such task: " + self.config["NAME"])
        print("\n\nEntering task : " + self.config["NAME"] + "\n\n")
        os.environ["CURRENT_TASK"] = self.config["NAME"]
        os.environ["SCRATCH"] = self.taskRoot
        os.environ["PROMPT"] = "{" + self.config["NAME"] +  "}"
        os.environ["__TASK__"] = self.config["NAME"]
        os.system("/bin/bash")
        return self

    def showTask(self):
        r"""
        Displays the status of a task
        """
        print("\n" + json.dumps(self.config, indent = 4) + "\n")
        return self

    def addChecklist(self, listItem):
	r"""
	Add a checklist item in a task.
	"""
	print("Adding checklist")
	if "Checklist" not in self.config.keys():
	    self.config["Checklist"] = []
	self.config["Checklist"].append({"Index" : len(self.config["Checklist"]), "Description" : listItem})
	open(self.configFile, "w").write(json.dumps(self.config, indent = 4))
        Tasks.refreshTasksData()
	return self

    def tickChecklist(self, itemNum):
	r"""
	Mark a checklist item in a task as complete
	"""
	try:
	    index = int(itemNum)
	except ValueError as e:
	    raise TasksException(str(itemNum) + " is not a valid integer. This argument needs to be an integer (the index of the checklist item)")
	if "Checklist" not in self.config.keys():
	    self.config["Checklist"] = []
	if index > (len(self.config["Checklist"]) - 1):
	    raise TasksException("Checklist item not present. Please enter a valid number.")
	del self.config["Checklist"][index]
	for i in range(0, len(self.config["Checklist"])):
	    self.config["Checklist"][i]["Index"] = i
	open(self.configFile, "w").write(json.dumps(self.config, indent = 4))
        Tasks.refreshTasksData()
	return self

    def archiveTask(self):
        r"""
        Archives the current Tasks folder and stores it in $HIME/.TasksArchives
        """
        if self.config["STATUS"].lower() == "complete":
            pwd = os.getcwd()
            os.chdir(self.taskRoot + "/../")
	    MiscUtils.debug(">> PWD changed to: " +  self.taskRoot)
            with tarfile.open(self.archiveFile, mode="w:gz") as archive:
                archive.add(self.taskName, recursive=True)
            os.chdir(pwd)
            if not os.path.isdir(Tasks.archiveRoot):
                os.makedirs(Tasks.archiveRoot)
            shutil.move(os.path.join(self.taskRoot + "/../", self.archiveFile), Tasks.archiveRoot + "/" + self.archiveFile)
            shutil.rmtree(self.taskRoot)
            Tasks.refreshTasksData()
        return self

    @staticmethod
    def getCurrentTask():
        if "CURRENT_TASK" in os.environ.keys():
            return Tasks(os.environ["CURRENT_TASK"])
        else:
            return None
        
    @staticmethod
    def refreshTasksData():
        open(Tasks.tasksData, "w").write(json.dumps([Tasks(t).config for t in os.listdir(Tasks.tasksRoot) if os.path.isdir(os.path.join(Tasks.tasksRoot, t))], indent = 4))

    @staticmethod
    def firstRun():
        if not os.path.isdir(Tasks.tasksRoot):
            os.makedirs(Tasks.tasksRoot)
	    

    @staticmethod
    def listTasks():
        Tasks.refreshTasksData()
        return json.loads(open(Tasks.tasksData, "r").read())
 
    @staticmethod
    def cleanTasks():
        [Tasks(t["NAME"]).archiveTask() for t in json.loads(open(Tasks.tasksData, "r").read())]
         

    @staticmethod
    def listArchived():
        print("\nArchived tasks:\n-----------------------------------")
        if os.path.isdir(Tasks.archiveRoot):
            count = 0
            for t in os.listdir(Tasks.archiveRoot):
                print("[" + str(count) + "] " + t.split(".")[0])
		count = count + 1
        print("\n")
        
    @staticmethod
    def controller(option = None, arg = None):
        if option == "new":
            if arg == None:
                raise TasksException("Did not provide name of new task in Tasks.controller")
            return Tasks(arg).createTask().enterTask()
        if option == "enter":
            if arg == None:
                raise TasksException("Did not provide name of task to enter in Tasks.controller")
            return Tasks(arg).enterTask()
        if option == "info":
            t = Tasks.getCurrentTask()
            if not t == None:
                t.showTask()
            else:
                print("Not in any task currently")
            return
        if option == "update":
            if arg == None:
                raise TasksException("Did not provide status string to update in Tasks.controller")
            t = Tasks.getCurrentTask()
            if t == None:
                print("\nNot in any task currently")
            else:
                t.updateTask(arg)
            return
	if option == "addChecklist":
	    if arg == None:
                raise TasksException("Did not provide the list item string")
            t = Tasks.getCurrentTask()
            if t == None:
                print("\nNot in any task currently")
            else:
                t.addChecklist(arg)
		os.system("clear")
		t.showTask()
            return
	if option == "tickChecklist":
	    if arg == None:
                raise TasksException("Did not provide the list item number")
            t = Tasks.getCurrentTask()
            if t == None:
                print("\nNot in any task currently")
            else:
                t.tickChecklist(arg)
		os.system("clear")
		t.showTask()
            return
        if option == "list":
            return Tasks.listTasks()
        if option == "listArchived":
            Tasks.listArchived()
            return
        if option == "clean":
            Tasks.cleanTasks()
            print("Cleaned...")
            Tasks.listTasks()
            return
        raise TasksException("Invalid option: " + option + "\n")

    @staticmethod
    def getOpts(cmdLineArgs):
	parser = argparse.ArgumentParser(prog = "Tasks", description = __doc__, usage = "Tasks [options]", formatter_class = argparse.RawTextHelpFormatter)
	parser.add_argument("-n", "--newTask", help = "Name of the new task")
	parser.add_argument("-e", "--enterTask", help = "Name of the task to enter")
	parser.add_argument("-u", "--updateTask", help = "String to represent the updated status of current task")
	parser.add_argument("-a", "--addChecklist", help = "Add a checklist item in the current task")
	parser.add_argument("-t", "--tickChecklist", help = "Tick a checklist item. Provide the integer index of the item in the list.")
	parser.add_argument("-c", "--clean", help = "Clean all tasks with status of 'Complete' (case ignored)", action = "store_true")
	parser.add_argument("-d", "--listArchived", help = "List all archived tasks", action = "store_true")
	parser.add_argument("-l", "--list", help = "List all active tasks", action = "store_true")
	parser.add_argument("-i", "--info", help = "Display info about current task", action = "store_true")
	parser.add_argument("-f", "--firstRun", help = "First run. Initializes folders, etc", action = "store_true")
	parser.add_argument("-r", "--restore", help = "Restore an archived task")
	args = parser.parse_args(cmdLineArgs)
	
	try:
	    if args.firstRun:
		Tasks.firstRun()
		return True
	    if args.list:
		print("\nActive tasks\n-----------------------------------")
		count = 0
		for t in Tasks.controller("list"):
		    print("[" + str(count) + "] " + t["NAME"] + " : " + t["STATUS"])
		    count = count + 1
		print("\n\n")
		return True
	    if args.listArchived:
		Tasks.controller("listArchived")
		return True
	    if args.clean:
		Tasks.controller("clean")
		return True
	    if args.newTask:
		Tasks.controller("new", args.newTask)
		return True
	    if args.enterTask:
		Tasks.controller("enter", args.enterTask)
		return True
	    if args.info:
		Tasks.controller("info")
		return True
	    if args.updateTask:
		Tasks.controller("update", args.updateTask)
		return True
	    if args.addChecklist:
		Tasks.controller("addChecklist", args.addChecklist)
		return True
	    if args.tickChecklist:
		Tasks.controller("tickChecklist", args.tickChecklist)
		return True
	except TasksException as e:
	    print("ERROR: " + str(e) + "\n\n")
	    parser.print_help()

     
