import curses
import boto3
import botocore

class Colours:
    TAG_COLOURS = 1
    INSTANCE_COLOURS = 2
    
class InstanceStatusWindow:
    def __init__(self, tagList, region, x, y, dx, dy):
	self.client = boto3.client("ec2", region_name = region)
	self.tagData = dict()
	for tag in tagList:
	    self.tagData[tag] = []
	self.window = curses.newwin(dy, dx, y, x)
	curses.init_pair(Colours.TAG_COLOURS, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(Colours.INSTANCE_COLOURS, curses.COLOR_BLACK, curses.COLOR_GREEN)

    def expandTags(self):
	for tag in self.tagData.keys():
	    try:
		response = self.client.describe_instances(
		    DryRun = False,
		    Filters=[
			{
			    "Name" : "tag-key",
			    'Values': [tag]
			},
		    ]
		)
		self.tagData[tag] = [instance for instances in response["Reservations"] for instance in instances["Instances"]]
	    except botocore.exceptions.ClientError as e:
		pass

    def displayInstances(self):
	self.window.clear()
	self.window.border(0)
	linum = 1
	colnum = 1
	for tag in self.tagData.keys():
	    self.window.addstr(linum, colnum, tag, curses.A_UNDERLINE)
	    linum = linum + 1
	    for instance in self.tagData[tag]:
		self.window.addstr(linum, colnum, instance["InstanceId"] + " : " + instance["State"]["Name"], curses.color_pair(Colours.INSTANCE_COLOURS))
		linum = linum + 1
	self.window.refresh()
	return self.window.getch()
	
	
    def refreshStatus(self):
	client = boto3.client("ec2")
	for i in self.instanceList:
	    response = client.describe_instance_status(
		DryRun = False,
		InstanceIds = self.instanceList,
		IncludeAllInstances = True
	    )


def mainLoop(stdscr):
    stdscr.clear()
    i = InstanceStatusWindow(["TYPE"], "us-east-1", 0, 0, curses.COLS - 1, curses.LINES - 1)
    i.expandTags()
    ch = i.displayInstances()
    while not ch == ord("q"):
	i.expandTags()
	ch = i.displayInstances()
	
    

if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.wrapper(mainLoop)
	    
