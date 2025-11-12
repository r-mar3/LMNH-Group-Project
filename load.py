"""Loads all local table data and uploads them to the RDS"""
import pyodbc
from os import environ
from dotenv import load_dotenv
import pandas as pd

DATA_FILEPATH = './data/clean_data/'
CSV_FILETYPE = '.csv'
TABLE_NAMES = [
    'license',
    'species',
    'image',
    'botanist',
    'plant',
    'country',
    'reading',
    'origin',
    'city'
]


def get_db_connection() -> pyodbc.Connection:
    """Returns a live connection to the database"""
    load_dotenv()
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 18 for SQL Server}};'
        f'SERVER={environ['DB_HOST']}, {environ['DB_PORT']};'
        f'DATABASE={environ['DB_NAME']};'
        f'UID={environ['DB_USER']};'
        f'PWD={environ['DB_PASSWORD']};'
        'TrustServerCertificate=yes;'
    )

    return conn


def load_csv(table_name: str) -> pd.DataFrame:
    """Returns a dataframe of the csv for a given table name"""
    return pd.read_csv(f'{DATA_FILEPATH}{table_name}{CSV_FILETYPE}')


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
        for table_name in TABLE_NAMES:
            table_df = load_csv(table_name)
            upload_table_data(connection, table_name, table_df)
