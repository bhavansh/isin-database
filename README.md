# ISIN-DB

[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

ISIN Database for ISIN Database for All NSE Traded Securities (Equity, Debt, ETF's, SGB, Mutual Funds).

## Installation
```bash
# Download the github repo and execute the cli by navigating inside the foler
python.exe .\cli.py query --query-name SEARCH_BY_ISIN
```

## Usage


```bash
# -------------------------------------------------------------------
(venv) PS E:\personal-projects\isin-database\isin_database> python.exe .\cli.py --help                                               
usage: cli.py [-h] {refresh-db,query,show-queries} ...

ISIN Database CLI

optional arguments:
  -h, --help            show this help message and exit

Commands:
  {refresh-db,query,show-queries}
    refresh-db          Refresh the database by locally downloading the csv files from github repository or from respective websites
    query               Query the database
    show-queries        Show all available queries with the required params

# ------------------------------------------------------------------- 
(venv) PS E:\personal-projects\isin-database\isin_database> python.exe .\cli.py refresh-db --help
usage: cli.py refresh-db [-h] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--log-file-path LOG_FILE_PATH] [--db-path DB_PATH] --csv-dir-path CSV_DIR_PATH

optional arguments:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Logging level (default: INFO)
  --log-file-path LOG_FILE_PATH
                        Path for log files
  --db-path DB_PATH     Path to the database
  --csv-dir-path CSV_DIR_PATH
                        Path to the CSV directory
# -------------------------------------------------------------------
(venv) PS E:\personal-projects\isin-database\isin_database> python.exe .\cli.py query --help     
usage: cli.py query [-h] --query-name {SEARCH_BY_ISIN,SEARCH_BY_ISIN_AND_CATEGORY,SEARCH_BY_AMFI_CODE,QUERY_ALL_DATA_FOR_ISIN} [--isin ISIN] [--symbol SYMBOL] [--category {equity,etf,debt,mf,sgb}] [--amfi-code AMFI_CODE]

optional arguments:
  -h, --help            show this help message and exit
  --query-name {SEARCH_BY_ISIN,SEARCH_BY_ISIN_AND_CATEGORY,SEARCH_BY_AMFI_CODE,QUERY_ALL_DATA_FOR_ISIN}
                        Name of the query to execute
  --isin ISIN           ISIN parameter for the query
  --symbol SYMBOL       Symbol parameter for the query
  --category {equity,etf,debt,mf,sgb}
                        Category parameter for the query
  --amfi-code AMFI_CODE
                        AMFI code parameter for the query


# -------------------------------------------------------------------
(venv) PS E:\personal-projects\isin-database\isin_database> python.exe .\cli.py show-queries
Showing available queries
-------------------------------------------
Query name: SEARCH_BY_ISIN                   :[':isin']
Query name: SEARCH_BY_ISIN_AND_CATEGORY      :[':symbol', ':category']
Query name: SEARCH_BY_AMFI_CODE              :[':amfi_code']
Query name: QUERY_ALL_DATA_FOR_ISIN          :[':category', ':isin']
-------------------------------------------


# -------------------------------------------------------------------
```

## Notes

- isin-database is shipped with a local database which may get obsolete over time. The local
database can be updated via the cli tool


Original Sources of the CSV Files 

```json
{
  "mf.csv"      : "https://portal.amfiindia.com/DownloadSchemeData_Po.aspx?mf=0",
  "active.csv"  : "https://nsearchives.nseindia.com/content/equities/List_of_Active_Securities_CM_DEBT.csv",
  "equity.csv"  : "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv",
  "etf.csv"     : "https://nsearchives.nseindia.com/content/equities/eq_etfseclist.csv",
  "debt.csv"    : "https://nsearchives.nseindia.com/content/equities/DEBT.csv",
  "sgb.xlsx"    : "https://rbidocs.rbi.org.in/rdocs/Content/DOCs/SOVERIGNGOLDBONDS.xlsx"
}
```

