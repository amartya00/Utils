r"""
Todo list data structure
"""

import sys
import os
import datetime

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../")
from libs.utils.MiscUtils import MiscUtils
from libs.account.CredsManager import CredsManager
from libs.utils.TimeUtils import TimeUtils, TimeUtilsException
from libs.utils.ToDoItem import TodoItem, TodoException

class TodoList:
    def __init__(self):
	self.data = {
	}

    def addItem(self, text, duedate):
	try:
	    item = TodoItem.getDefaultItem()
	    item.setter(
		{
		    "Description" : text,
		    "DueDate" : duedate
		}
	    )
	    item.data["Id"] = item.computeId()
	    self.data[item.data["Id"]] = item
	except ValueError as e:
	    raise TodoException("Please enter values in correct format: " + str(e))
	return self

    def deleteItem(self, itemId):
	if not itemId in self.data.keys():
	    raise TodoException("Invalid id: " + itemId)
	else:
	    del(self.data[itemId])
	return self

    def updateItem(self, todoId, dueDate = None, status = None):
	if not todoId in self.data.keys():
	    raise TodoException("Invalid id: " + todoId)
	else:
	    self.data[todoId].setter(
		{
		    "Status" : status,
		    "DueDate" : dueDate,
		    "LastModified" : datetime.datetime.now().strftime(TimeUtils.validformats[0])
		}
	    )
	return self

    def clean(self):
	itemsToDelete = []
	for k in self.data.keys():
	    if self.data[k].data["Status"].lower() in ["complete", "done", "finished", "canceled"]:
		itemsToDelete.append(k)
	for i in itemsToDelete:
	    MiscUtils.debug("Deleting: " + self.data[i].data["Description"])
	    self.deleteItem(i)

    def toMap(self):
	retval = {}
	for k in self.data.keys():
	    retval[k] = self.data[k].data
	return retval

    def mergeFromMap(self, data):
	for i in data.keys():
	    if i not in self.data.keys():
		self.data[i] = TodoItem()
		self.data[i].setter(data[i])
		self.data[i].setter({"Id" : i})
	return self

    def merge(self, data):
	for i in data.data.keys():
	    if i not in self.data.keys():
		self.data[i] = data.data[i]
		self.data[i].setter({"Id" : i})
	    else:
		MiscUtils.debug("Skipping merging todo: " + data.data[i].data["Description"])
	return self

    def toLists(self, sortKey = "DueDate"):
	headers = ["Description", "CreateDate", "DueDate", "Status", "LastModified", "Id"]
	if sortKey not in headers:
	    MiscUtils.warn("Cannot sort by '" + sortKey + "' (no such field). Just sorting by 'DueDate'.")
	    sortKey = "DueDate"
	table = []
	for k in self.data.keys():
	    table.append(self.data[k].toList())
	table.sort(key = lambda e: e[headers.index(sortKey)], reverse = False)
	retval = [headers]
	retval.extend(table)
	return retval
	
    def backfill(self):
	for k in self.data.keys():
	    self.data[k].backfill()
	return self
