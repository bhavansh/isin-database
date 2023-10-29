#  Copyright (c) 2023. Bhavansh Gupta.
import sqlite3

from isin_database.utils import get_isin_db_path


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class INDISINDb:
    """A Comprehensive Database for ISIN Codes of all the securities listed in Indian Markets
        (Equity, Debt, ETF's, SGB, Mutual Funds, etc.)
    """
    connection = None
    cursor = None

    queries = {
        'SEARCH_BY_ISIN' : 'SELECT mappimg from isin_consolidated WHERE isin = :isin'
    }

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def initialize(self):
        """Initialize database."""
        self.connection = sqlite3.connect(get_isin_db_path())
        self.connection.row_factory = dict_factory
        self.cursor = self.connection.cursor()

    def close(self):
        """Close database connection."""
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def run_query(self, sql, arguments, fetchone=False):
        self_initialized = False
        if self.connection is None:
            self.initialize()
            self_initialized = True
        try:
            self.cursor.execute(sql, arguments)
            if fetchone:
                return self.cursor.fetchone()
            return self.cursor.fetchall()
        finally:
            if self_initialized:
                self.close()

    def search_by_isin(self, isin: str):
        """
        Lookup scheme data via ISIN code
        :param isin: Fund ISIN
        :return:
        """
        return self.run_query(sql, {'isin':isin})
