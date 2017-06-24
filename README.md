# Utils app:
This contains a bunch of small utilities

## Pre-requisites:
To get it running you need to install pip first and install pytz, boto3 and ntplib.

## Components:
There are 2 main components in the tool

### CredsManager
This module manages profiles that the user can create and maintain. Each profile will consist of a name and AWS credentials.
On the first run, a 'DEFAULT' profile is created withn no credentials. When the CredeManager does not find credentials, it tries to revert to system default aws credentials.
The main job of this module is to supply credential information based on profile name that other modules ask for.
For more help on usage run "UtilsApp CredsManager -h"

### ToDo
This module is a to-do application, that syncs via S3. This makes use of profile and creds information from the CredsManager.
The local copy of the Todo json file is saved in ~/.Todo/<PROFILE_NAME>_Todo.json. The config file is saved in ~/.<PROFILE_NAME>_config.
This can save Todo lists for multiple profiles that the user creates. By default, it resorts to a profile named 'DEFAULT'
For more help on usage run "UtilsApp Todo -h"

## Installation:
Currently installation can be done in 2 ways:
* If you have codedeploy setup, the package includes the appspec file.
* You can build and install:
** Clone the repo.
** create a build folder and run cmake.
** make && sudo make install.
