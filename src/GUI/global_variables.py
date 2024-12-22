import configparser

from src.utils.logging_util import logger
from src.utils.find_path_to_config import find_config


global_variables_state: dict = {
    "logger": logger,
}

global_variables_state["config"] = configparser.ConfigParser()
global_variables_state["config"].read(find_config())
