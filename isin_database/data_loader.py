#  Copyright (c) 2023. Bhavansh Gupta.
import logging
import concurrent.futures
import threading

import pandas as pd

from isin_database import INDISINDb
from isin_database.utils import (
    get_csv_data_dir_path,
    load_data_in_dataframe,
    setup_logging,
    Counter, get_log_path
)

data_file_list = [
    "active.csv",
    "debt.csv",
    "equity.csv",
    "etf.csv",
    "mf.csv",
    "sgb.xlsx",
]


def format_column_names(df):
    df.columns = [
        "ISIN" if "ISIN" in col.upper() else col.upper().strip() for col in df.columns
    ]
    return df


def format_dataframe(df: pd.DataFrame, filename):
    if filename in ["equity.csv", "etf.csv"]:
        df = format_column_names(df)
        return df
    elif filename == "mf.csv":
        df = format_column_names(df)
        df["ISIN"].fillna("", inplace=True)
        df["ISIN"] = df["ISIN"].str.strip()
        df["ISIN"] = df["ISIN"].str.replace("-", "")
        df["ISIN"] = df["ISIN"].str.replace(" ", "")
        for index, row in df.iterrows():
            if len(row["ISIN"]) % 12 == 2 and row["ISIN"].endswith("NA"):
                df.at[index, "ISIN"] = row["ISIN"].replace("NA", "")
            if len(row["ISIN"]) % 12 != 0:
                if not row["ISIN"].startswith("IN"):
                    df.at[index, "ISIN"] = ""
        return df
    elif filename == "active.csv":
        df.set_index(df.columns[0], inplace=True)
        df = format_column_names(df)
        return df
    elif filename == "debt.csv":
        # Custom changes to fix the debt.csv file and add ISIN code
        column_names = df.columns.tolist() + ["ISIN"]
        df.insert(0, "symbol_", df.index)
        df.columns = column_names
        df = format_column_names(df)
        df.reset_index(drop=True, inplace=True)
        return df
    elif filename == "sgb.xlsx":
        # Custom settings for sgb.xlsx file
        df.drop(df.columns[0], axis=1, inplace=True)
        df.columns = df.iloc[1].to_list()
        df = format_column_names(df)
        df.drop([0, 1], inplace=True)
        df.set_index(df.columns[0], inplace=True)
        return df


# Debt ->  SYMBOL-SERIES
# Equity, ETF -> SYMBOL
# SGB, MF - No SYMBOL
# MF ISIN is split in two where more than 1 isin-codes are present for consolidated_isin_df

def create_consolidated_isin_df(file_df_map: dict):
    consolidated_isin_df = pd.DataFrame(
        columns=["ISIN", "SYMBOL", "NAME", "CATEGORY", "IS_IN_ACTIVE"]
    )
    # active_df = file_df_map["active"]
    # consolidated_isin_df["ISIN"] = active_df["ISIN"]
    # consolidated_isin_df["NAME"] = active_df["COMPANY NAME"]
    # consolidated_isin_df["IS_IN_ACTIVE"] = True

    def process_row(row, category):
        logging.debug(
            f"{Counter.incr()}:{threading.current_thread().name}  Processing category: {category} --- isin : {row['ISIN']}"
        )
        isin = row["ISIN"]

        if category == "debt":
            if not pd.isna(row["SERIES"]):
                symbol = row["SYMBOL"] + "-" + row["SERIES"]
            else:
                symbol = row.get("SYMBOL", None)
        elif category in ["equity", "etf"]:
            symbol = row.get("SYMBOL", None)
        else:
            symbol = None

        if category in ["debt", "equity", "etf", "sgb"]:
            name = row.get(
                "NAME OF COMPANY", row.get("SECURITY NAME", row.get("TRANCHE"))
            )
        else:
            name = row["SCHEME NAV NAME"]

        return pd.Series(
            {
                "ISIN": isin,
                "SYMBOL": symbol,
                "NAME": name,
                "CATEGORY": category,
                "IS_IN_ACTIVE": False,
            }
        )

    def process_file(key, file_df):
        logging.info("Creating consolidated isin database for {}".format(key))
        series_list = []
        for _, row in file_df.iterrows():
            if key == "mf" and len(row["ISIN"]) > 12:
                isin_list = [
                    row["ISIN"][i: i + 12] for i in range(0, len(row["ISIN"]), 12)
                ]
                for isin_chunk in isin_list:
                    series_list.append(process_row(row, key))
            else:
                series_list.append(process_row(row, key))
        return series_list

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(process_file, key, file_df_map[key]): key
            for key in file_df_map
            if key != "active"
        }

        for future in concurrent.futures.as_completed(futures):
            key = futures[future]
            result_series_list = future.result()
            result_df = pd.DataFrame.from_records(result_series_list)
            logging.info("Converting Series to Dataframe")
            consolidated_isin_df = pd.concat(
                [consolidated_isin_df, result_df], axis=0, ignore_index=True
            )

    return consolidated_isin_df


def refresh_db():
    file_df_map = {}
    for filename in data_file_list:
        logging.info("Loading file: {} as dataframe".format(filename))
        df = load_data_in_dataframe(get_csv_data_dir_path() / filename)
        logging.info("Formatting dataframe: {}".format(filename.split(".")[0]))
        df = format_dataframe(df, filename)
        file_df_map[filename.split(".")[0]] = df
        with INDISINDb() as isin_db:
            logging.info("Recording dataframe as db: {}".format(filename.split(".")[0]))
            df.to_sql(
                filename.split(".")[0], isin_db.connection, if_exists="replace", index=False
            )

    logging.info("Creating consolidated isin database")
    consolidated_isin_df = create_consolidated_isin_df(file_df_map)
    with INDISINDb() as isin_db:
        consolidated_isin_df.to_sql(
            "consolidated_isin", isin_db.connection, if_exists="replace", index=False
        )


if __name__ == "__main__":
    setup_logging("INFO", get_log_path())
    refresh_db()
