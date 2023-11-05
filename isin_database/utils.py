#  Copyright (c) 2023. Bhavansh Gupta.
import logging
import os
import pathlib
from logging.handlers import TimedRotatingFileHandler

import pandas as pd

# Define default paths
BASE_DIR = pathlib.Path(__file__).resolve().parent
INTERNAL_ISIN_DB_PATH = BASE_DIR / "isin.db"
INTERNAL_CSV_DATA_DIR_PATH = BASE_DIR.parent / "csv-data"
INTERNAL_LOG_DIR_PATH = BASE_DIR.parent / "logs"


# Generic Methods to access Paths for files and db

def get_log_path(path=""):
    return get_path(path, True, INTERNAL_LOG_DIR_PATH)


def get_isin_db_path(path=""):
    return get_path(path, False, INTERNAL_ISIN_DB_PATH)


def get_csv_data_dir_path(path=""):
    return get_path(path, True, INTERNAL_CSV_DATA_DIR_PATH)


def get_path(path: str, is_dir: bool, default_path: pathlib.Path):
    try:
        if is_dir:
            if os.path.exists(path) and os.path.isdir(path):
                return pathlib.Path(path)
        else:
            if os.path.exists(path) and os.path.isfile(path):
                return pathlib.Path(path)
    except TypeError:
        pass
    return default_path


# Generic Methods to load dataframe from csv, excel
def load_data_in_dataframe(path: pathlib.Path):
    if path.suffix == ".csv":
        dataframe = pd.read_csv(path, encoding="ISO-8859-1")
    elif path.suffix == ".xlsx":
        dataframe = pd.read_excel(path)
    else:
        return
    dataframe.columns = dataframe.columns.str.strip()
    return dataframe


LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


# Setup logging & debugging utils
def setup_logging(log_level="INFO", log_folder=INTERNAL_LOG_DIR_PATH):
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    log_level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_file_name = pathlib.Path(log_folder) / "isin-database.log"

    log_handler = TimedRotatingFileHandler(
        filename=log_file_name,  # Base filename
        when="midnight",  # Rotate daily at midnight
        interval=1,  # Create a new log file daily
        backupCount=7,  # Keep up to 7 days of logs
    )

    log_handler.setFormatter(log_formatter)

    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(log_handler)


class Counter:
    _count = 0  # Initialize the counter as a class variable

    @staticmethod
    def incr():
        Counter._count += 1
        return Counter._count

    @staticmethod
    def reset():
        Counter._count = 0


def add_space(string: str, length: int):
    return " " * (length - len(string))
