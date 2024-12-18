import configparser

from src.utils.logging_util import LoggerManager
from src.utils.find_path_to_config import find_config


global_variables_state: dict = {
    "logger":LoggerManager(),
    "config": configparser.ConfigParser()
}


global_variables_state["config"].read(find_config())
