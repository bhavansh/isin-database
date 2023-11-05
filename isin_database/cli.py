#  Copyright (c) 2023. Bhavansh Gupta.
import argparse
import logging
import re

from ind_isin import INDISINDb
from utils import setup_logging, get_log_path, add_space


def main():
    # Create the main parser
    parser = argparse.ArgumentParser(description='ISIN Database CLI')

    # Subparsers for different commands
    subparsers = parser.add_subparsers(title='Commands', dest='command')

    # Subparser for 'refresh-db' command
    refresh_db_parser = subparsers.add_parser('refresh-db', help="Refresh the database by locally downloading "
                                                                 "the csv files from github repository or from "
                                                                 "respective websites")

    refresh_db_parser.add_argument('--log-level', default='INFO',
                                   choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                                   help='Logging level (default: INFO)')
    refresh_db_parser.add_argument('--log-file-path', help='Path for log files', default="")
    refresh_db_parser.add_argument('--db-path', help='Path to the database', default="")
    refresh_db_parser.add_argument('--csv-dir-path', help='Path to the CSV directory', required=True)

    # Subparser for 'query' command
    query_parser = subparsers.add_parser('query', help='Query the database')
    query_parser.add_argument('--query-name', required=True, help='Name of the query to execute',
                              choices=INDISINDb.queries)
    query_parser.add_argument('--isin', help='ISIN parameter for the query')
    query_parser.add_argument('--symbol', help='Symbol parameter for the query')
    query_parser.add_argument('--category', help='Category parameter for the query',
                              choices=['equity', 'etf', 'debt', 'mf', 'sgb'])
    query_parser.add_argument('--amfi-code', help='AMFI code parameter for the query')

    # Subparser for 'show_available_queries' command
    show_queries_parser = subparsers.add_parser('show-queries',
                                                help='Show all available queries with the required params')

    # Parse the command line arguments

    args = parser.parse_args()

    # You can access the values of the arguments using args.refresh_db, args.log_level, etc.
    # Now, you can access the arguments based on the selected subcommand
    if args.command == 'refresh-db':
        print(f'Refreshing the database with log-level: {args.log_level}')
        print(f'Log file path: {args.log_file_path}')
        print(f'Database path: {args.db_path}')
        print(f'CSV directory path: {args.csv_dir_path}')
    elif args.command == 'query':
        print("-------------------------------------------")
        print(f'Executing query: {args.query_name}')
        print("Parameters: [", end=" ")
        print(f'isin: {args.isin}', end=", ")
        print(f'symbol: {args.symbol}', end=", ")
        print(f'category: {args.category}', end=", ")
        print(f'amfi_code: {args.amfi_code}', end=" ")
        print("]")
        print("-------------------------------------------")

        with INDISINDb() as isin_db:
            result = isin_db.search_by_query(query_name=args.query_name, isin=args.isin, symbol=args.symbol,
                                             category=args.category, code=args.amfi_code, db=args.category)
            print(result)
        print("-------------------------------------------")

    elif args.command == 'show-queries':
        print('Showing available queries')
        print("-------------------------------------------")
        for key, value in INDISINDb.queries.items():
            placeholders = re.findall(r':\w+', value)
            # query_args = [p for p in placeholders if p != ':db']
            query_args = [":category" if p == ':db' else p for p in placeholders]

            print(f"Query name: {key} {add_space(key, 30)}  :{query_args}")
        print("-------------------------------------------")

    else:
        parser.print_help()
        parser.print_usage()

    setup_logging("INFO", get_log_path(""))


if __name__ == "__main__":
    main()
