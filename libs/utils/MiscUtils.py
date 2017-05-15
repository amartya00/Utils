r"""
This contains some miscelenous utilities
"""

import os

class MiscUtils:
    @staticmethod
    def debug(message):
	if "DEBUG_MODE" in os.environ.keys() and os.environ["DEBUG_MODE"] == "true":
	    print("[DEBUG] " + message)

    @staticmethod
    def info(message):
	print("[INFO] " + message)

    @staticmethod
    def error(message):
	print("[ERROR] " + message)
