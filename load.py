# pylint: disable=c-extension-no-member

"""Loads all local table data and uploads them to the RDS"""
from os import environ
from dotenv import load_dotenv
import pandas as pd
import pyodbc
import numpy as np

DATA_FILEPATH = './data/clean_data.csv'
BASE_TABLES = [
    'country',
    'botanist',
    'license'
]

FOREIGN_TABLES = [
    'city',
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


def upload_table_data(conn: pyodbc.Connection, table_name: str, df: pd.DataFrame, unique_col: str) -> None:
    """Uploads the data in the given dataframe to the matching table in the database"""
    columns = list(df.columns)
    column_names = ', '.join(columns)
    column_placeholders = ', '.join('?' for _ in columns)
    sql_query = f"""
        INSERT INTO
            {table_name} ({column_names})
        SELECT
            {column_placeholders}
        WHERE NOT EXISTS
            (SELECT 1 FROM {table_name} WHERE {unique_col} = ?)
        ;
    """

    df = df.dropna().reset_index()

    something_strange = []
    for index, row in enumerate(df.to_numpy()):

        something_strange.append(
            tuple(np.append(row[1:], df[unique_col][index])))

    cur = conn.cursor()
    cur.executemany(
        sql_query, something_strange)
    cur.close()


if __name__ == '__main__':
    clean_table = pd.read_csv(DATA_FILEPATH)
    tables = {}

    # refactor to a function
    columns = clean_table.columns.tolist()

    for tablename in BASE_TABLES:
        tables[tablename] = {
            'columns': [col for col in columns if tablename + '_' in col],
            'unique': [col for col in columns if '_name' in col]
        }

    # for tablename in FOREIGN_TABLES:  # add a list of foreign col names for add 'foreign'+_id
    #     tables[tablename] = [col for col in columns if tablename + '_' in col]

    with get_db_connection() as connection:
        # add base tables with auto generated ids
        for table_name, columns in tables.items():

            upload_table_data(connection, table_name,
                              clean_table[columns], unique_col=)
