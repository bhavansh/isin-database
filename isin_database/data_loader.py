#  Copyright (c) 2023. Bhavansh Gupta.
import logging

import pandas as pd

from isin_database import INDISINDb
from isin_database.utils import (
    get_csv_data_dir_path,
    load_data_in_dataframe,
    setup_logging,
)

data_file_list = [
    "active.csv",
    # "debt.csv",
    # "equity.csv",
    # "etf.csv",
    "mf.csv",
    # "sgb.xlsx",
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
    active_df = file_df_map["active"]

    consolidated_isin_df["ISIN"] = active_df["ISIN"]
    consolidated_isin_df["NAME"] = active_df["COMPANY NAME"]
    consolidated_isin_df["IS_IN_ACTIVE"] = True

    for key in file_df_map.keys():
        logging.info("Creating consolidated isin database for {}".format(key))
        if key == "debt":
            for _, row in file_df_map[key].iterrows():
                consolidated_isin_df = add_record_to_consolidated_isin_df(
                    consolidated_isin_df,
                    row["ISIN"],
                    row["SYMBOL"] + "-" + row["SERIES"],
                    row["NAME OF COMPANY"],
                    "debt",
                )
        elif key == "equity":
            for _, row in file_df_map[key].iterrows():
                consolidated_isin_df = add_record_to_consolidated_isin_df(
                    consolidated_isin_df,
                    row["ISIN"],
                    row["SYMBOL"],
                    row["NAME OF COMPANY"],
                    "equity",
                )
        elif key == "etf":
            for _, row in file_df_map[key].iterrows():
                consolidated_isin_df = add_record_to_consolidated_isin_df(
                    consolidated_isin_df,
                    row["ISIN"],
                    row["SYMBOL"],
                    row["SECURITY NAME"],
                    "etf",
                )
        elif key == "sgb":
            for _, row in file_df_map[key].iterrows():
                consolidated_isin_df = add_record_to_consolidated_isin_df(
                    consolidated_isin_df,
                    row["ISIN"],
                    None,
                    row["TRANCHE"],
                    "sgb",
                )
        elif key == "mf":
            counter = 0
            for _, row in file_df_map[key].iterrows():
                if len(row["ISIN"]) <= 12:
                    consolidated_isin_df = add_record_to_consolidated_isin_df(
                        consolidated_isin_df,
                        row["ISIN"],
                        None,
                        row["SCHEME NAV NAME"],
                        "mf",
                    )
                elif len(row["ISIN"]) > 12:
                    isin_codes = row["ISIN"]
                    isin_list = [
                        isin_codes[i: i + 12] for i in range(0, len(isin_codes), 12)
                    ]
                    for isin in isin_list:
                        consolidated_isin_df = add_record_to_consolidated_isin_df(
                            consolidated_isin_df,
                            isin,
                            None,
                            row["SCHEME NAV NAME"],
                            "mf",
                        )
    return consolidated_isin_df


def add_record_to_consolidated_isin_df(
        df: pd.DataFrame, isin: str, symbol: str, name: str, category: str
):
    if isin in df:
        # Get the index where ISIN matches
        idx = df.index[df["ISIN"] == isin].tolist()[0]
        df.at[idx, "CATEGORY"] = category
        df.at[idx, "SYMBOL"] = symbol
    else:
        new_row = pd.DataFrame(
            {
                "ISIN": [isin],
                "SYMBOL": [symbol],
                "NAME": [name],
                "CATEGORY": [category],
                "IS_IN_ACTIVE": [False],
            }
        )
        df = pd.concat([df, new_row], ignore_index=True)
    return df


setup_logging()
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
    setup_logging()
