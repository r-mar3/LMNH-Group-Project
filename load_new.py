# pylint: disable=c-extension-no-member

"""Loads all local table data and uploads them to the RDS"""
from os import environ
from dotenv import load_dotenv
import pandas as pd
import pyodbc

DATA_FILEPATH = './data/clean_data.csv'
BASE_TABLES = [
    'country',
    'license',
    'botanist'
]
MERGE_TABLES = [
    'city'
    'origin',
    'image',
    'species',
    'plant',
    'reading'  # keep adding rows to this, allow duplicates!
]


def get_db_connection() -> pyodbc.Connection:
    """Returns a live connection to the database"""
    load_dotenv()
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={environ['DB_HOST']}, {environ['DB_PORT']};"
        f"DATABASE={environ['DB_NAME']};"
        f"UID={environ['DB_USER']};"
        f"PWD={environ['DB_PASSWORD']};"
        'TrustServerCertificate=yes;'
    )

    return conn


def upload_table_data(conn: pyodbc.Connection, table_name: str, df: pd.DataFrame) -> None:
    """Uploads the data in the given dataframe to the matching table in the database"""
    columns = list(df.columns)
    column_names = ', '.join(columns)
    column_placeholders = ', '.join('?' for _ in columns)
    sql_query = f"""
        INSERT INTO
            {table_name} ({column_names})
        VALUES
            ({column_placeholders});
    """

    cur = conn.cursor()
    cur.executemany(sql_query, [tuple(row) for row in df.to_numpy()])
    cur.close()


if __name__ == '__main__':
    with get_db_connection() as connection:
        clean_table = pd.read_csv(DATA_FILEPATH)

        # add base tables with auto generated ids
        for table in BASE_TABLES:
            upload_table_data(connection, table, clean_table)
