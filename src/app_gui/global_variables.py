
from src.utils.logging_util import LoggerManager
import queue
import threading
import configparser
import sys
from pathlib import Path


global_variables_state:dict={
    "logger":LoggerManager.get_logger,
    "data_queue" : queue.Queue(),
    "connection_status_flag":threading.Event(),
    "config": configparser.ConfigParser()
}


if hasattr(sys, "_MEIPASS"):
    PROJ_ROOT = Path(getattr(sys, "_MEIPASS"))
else:
    PROJ_ROOT = Path(__file__).resolve().parent

config_path =  Path(r'C:\Users\A\skyView')

global_variables_state["config"].read(config_path)