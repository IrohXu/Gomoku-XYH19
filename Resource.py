import sys
import os

RESOURCE_DIR = os.path.abspath(".")
if getattr(sys, 'frozen', False): #是否Bundle Resource
    RESOURCE_DIR = sys._MEIPASS
        