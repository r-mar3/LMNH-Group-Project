# pylint: disable=c-extension-no-member

"""Loads all local table data and uploads them to the RDS"""
from os import environ
from dotenv import load_dotenv
import pandas as pd
import pyodbc
import numpy as np
from pprint import pprint

DATA_FILEPATH = './data/clean_data.csv'
# BASE_TABLES = [
#     'country',
#     'botanist',
#     'license'
# ]

# FOREIGN_TABLES = [
#     'city',
#     'origin',
#     'image',
#     'species',
#     'plant',
#     'reading'  # keep adding rows to this, allow duplicates!
# ]

TABLES = {
    'country': {
        'columns': ['country_name'],
        'unique_column': 'country_name'
    },
    'botanist': {
        'columns': ['botanist_name', 'botanist_email', 'botanist_phone'],
        'unique_column': 'botanist_email'
    },
    'license': {
        'columns': ['license_name', 'license_number', 'license_url'],
        'unique_column': 'license_number'
    }
}

FOREIGN_TABLES = {
    'city': {
        'columns': ['city_name', 'country_id'],
        'unique_column': 'city_name'
    },
    'origin': {
        'columns': ['origin_longitude', 'origin_latitude', 'city_id'],
        'unique_column': ['origin_longitude', 'origin_latitude']
    },
    'image': {
        'columns': ['image_original_url', 'image_regular_url', 'image_medium_url', 'image_small_url', 'image_thumbnail_url', 'license_id'],
        'unique_column': 'image_original_url'
    },
    'species': {
        'columns': ['species_name', 'species_scientific_name', 'image_id'],
        'unique_column': 'species_name'
    },
    'plant': {
        'columns': ['plant_id', 'species_id', 'origin_id'],
        'unique_column': 'plant_id'
    },
    'reading': {
        'columns': ['reading_last_watered', 'reading_time_taken', 'reading_soil_moisture', 'reading_temperature', 'reading_error', 'botanist_id', 'plant_id'],
        'unique_column': ''
    }

}


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


def upload_table_data_with_foreign_key(conn: pyodbc.Connection) -> None:
    sql_query = """
        INSERT INTO
            city (city_name, country_id)
        SELECT
            city_name, country_id
        WHERE
    """


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
    print(sql_query)
    input()
    df = df.dropna().reset_index()

    # params for executemany must be a tuple, and must include the
    # values we want to insert, and the unique value to check against
    # e.g. ('Albania', 'Albania') inserts Albania only if Albania doesn't exist
    sql_params = []
    for index, row in enumerate(df.to_numpy()):
        sql_params.append(tuple(np.append(row[1:], df[unique_col][index])))

    cur = conn.cursor()
    cur.executemany(sql_query, sql_params)
    cur.close()


if __name__ == '__main__':
    clean_table = pd.read_csv(DATA_FILEPATH)
    # tables = {}

    # refactor to a function
    # columns = clean_table.columns.tolist()

    # for tablename in BASE_TABLES:
    #     tables[tablename] = {
    #         'columns': [col for col in columns if tablename + '_' in col],
    #         'unique': [col for col in columns if '_name' in col]
    #     }

    # for tablename in FOREIGN_TABLES:  # add a list of foreign col names for add 'foreign'+_id
    #     tables[tablename] = [col for col in columns if tablename + '_' in col]

    with get_db_connection() as connection:
        # add base tables with auto generated ids
        # for table_name, columns in tables.items():
        #     upload_table_data(connection, table_name,
        #                       clean_table[columns], unique_col=)
        for table in TABLES:
            print(table)
            upload_table_data(
                connection, table, clean_table[TABLES[table]['columns']], TABLES[table]['unique_column'])
