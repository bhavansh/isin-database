#  Copyright (c) 2023. Bhavansh Gupta.
import logging
import os
import pathlib

import pandas as pd

# Define default paths
BASE_DIR = pathlib.Path(__file__).resolve().parent
INTERNAL_ISIN_DB_PATH = BASE_DIR / "isin.db"
INTERNAL_CSV_DATA_DIR_PATH = BASE_DIR.parent / "csv-data"


# Generic Methods to access Paths for files and db
def get_isin_db_path():
    return get_path("INDISIN_DB", False, INTERNAL_ISIN_DB_PATH)


def get_csv_data_dir_path():
    return get_path("INDISIN_CSV_DATA_DIR", True, INTERNAL_CSV_DATA_DIR_PATH)


def get_path(env_key: str, is_dir: bool, default_path: pathlib.Path):
    env = os.getenv(env_key)
    try:
        if is_dir:
            if os.path.exists(env) and os.path.isdir(env):
                return pathlib.Path(env)
        else:
            if os.path.exists(env) and os.path.isfile(env):
                return pathlib.Path(env)
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


# Setup logging utils
def setup_logging():
    logging.basicConfig(
        filename="isin-database.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
