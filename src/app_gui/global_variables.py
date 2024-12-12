
from src.utils.logging_util import LoggerManager
import queue
import threading
import configparser
import sys
from pathlib import Path



def find_config():
        if hasattr(sys, "_MEIPASS"):
            PROJ_ROOT = Path(getattr(sys, "_MEIPASS"))
        else:
            PROJ_ROOT = Path(r'C:\Users\A\skyView')
            
        return PROJ_ROOT / 'config.ini'


global_variables_state:dict={
    "logger":LoggerManager(),
    "data_queue" : queue.Queue(),
    "connection_status_flag":threading.Event(),
    "config": configparser.ConfigParser()
}


global_variables_state["config"].read(find_config())
