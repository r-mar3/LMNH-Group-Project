# pylint: disable=c-extension-no-member

"""Loads all local table data and uploads them to the RDS"""
from os import environ
from dotenv import load_dotenv
import pandas as pd
import pyodbc
import numpy as np
from datetime import datetime
from pprint import pprint

DATA_FILEPATH = './data/clean_data.csv'

TABLES = [
    {
        'table_name': 'country',
        'columns': ['country_name'],
        'unique_column': 'country_name'
    },
    {
        'table_name': 'botanist',
        'columns': ['botanist_name', 'botanist_email', 'botanist_phone'],
        'unique_column': 'botanist_email'
    },
    {
        'table_name': 'license',
        'columns': ['license_name', 'license_number', 'license_url'],
        'unique_column': 'license_number'
    }
]

FOREIGN_TABLES = [
    {
        'table_name': 'city',
        'columns': ['city_name', 'country_id'],
        'unique_column': 'city_name'
    },
    {
        'table_name': 'origin',
        'columns': ['origin_longitude', 'origin_latitude', 'city_id'],
        'unique_column': 'origin_longitude'
    },
    {
        'table_name': 'image',
        'columns': ['image_original_url', 'image_regular_url', 'image_medium_url', 'image_small_url', 'image_thumbnail_url', 'license_id'],
        'unique_column': 'image_original_url'
    },
    {
        'table_name': 'species',
        'columns': ['species_name', 'species_scientific_name', 'image_id'],
        'unique_column': 'species_name'
    },
    {
        'table_name': 'plant',
        'columns': ['plant_id', 'species_id', 'origin_id'],
        'unique_column': 'plant_id'
    },
    {
        'table_name': 'reading',
        'columns': ['reading_last_watered', 'reading_time_taken', 'reading_soil_moisture', 'reading_temperature', 'reading_error', 'reading_alert', 'plant_id', 'botanist_id'],
        'unique_column': 'reading_time_taken'
    }

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


def upload_table_data_with_foreign_key(conn: pyodbc.Connection, table_dict: dict, df: pd.DataFrame) -> None:
    # all column names
    columns = table_dict['columns']
    column_names = ', '.join(columns)

    if table_dict['table_name'] == 'reading':
        local = [col for col in columns if not col.endswith(
            '_id')]
        all_foreign_keys = [
            col for col in columns if col.endswith('_id')]
    else:
        # column names which only appear in this table
        local = [col for col in columns if not col.endswith(
            '_id') or col == 'plant_id']
        # foreign table names which are mentioned
        all_foreign_keys = [
            col for col in columns if col.endswith('_id') and col != 'plant_id']

    column_placeholders = ', '.join('?' for _ in local)
    table_name = table_dict['table_name']
    unique_col = table_dict['unique_column']

    sql_query = f"""
        INSERT INTO
            {table_name} ({column_names})
        SELECT
            {column_placeholders},
            """

    all_foreign_unique_columns = local
    for foreign_key in all_foreign_keys:
        foreign_name = foreign_key.replace('_id', '')

        for table in FOREIGN_TABLES:
            if table['table_name'] == foreign_name:
                foreign_table = table
                all_foreign_unique_columns.append(table['unique_column'])

        for table in TABLES:
            if table['table_name'] == foreign_name:
                foreign_table = table
                all_foreign_unique_columns.append(table['unique_column'])

        sql_query += f"""(SELECT
                {foreign_key}
            FROM
                {foreign_table['table_name']}
            WHERE
                {foreign_table['unique_column']} = ?),"""
    sql_query = sql_query[:-1]

    sql_query += f"""
        WHERE NOT EXISTS
            (SELECT 1 FROM {table_name} WHERE {unique_col} = ?);"""

    df = df[all_foreign_unique_columns]
    if table_dict['table_name'] != 'reading':
        df = df.dropna().reset_index()
    else:
        df = df.fillna(np.nan).replace([np.nan], None)

        df['reading_last_watered'] = pd.to_datetime(
            df['reading_last_watered'])

        df['reading_time_taken'] = pd.to_datetime(
            df['reading_time_taken'])

    # params for executemany must be a tuple, and must include the
    # values we want to insert, and the unique value to check against
    # e.g. ('Albania', 'Albania') inserts Albania only if Albania doesn't exist
    sql_params = []
    for index, row in enumerate(df.to_numpy()):
        if table_dict['table_name'] == 'reading':
            sql_params.append(tuple(np.append(row, df[unique_col][index])))
        else:
            sql_params.append(tuple(np.append(row[1:], df[unique_col][index])))

    cur = conn.cursor()
    cur.executemany(sql_query, sql_params)
    cur.close()


def upload_table_data(conn: pyodbc.Connection, table_dict: dict, df: pd.DataFrame) -> None:
    """Uploads the data in the given dataframe to the matching table in the database"""
    columns = table_dict['columns']
    column_names = ', '.join(columns)
    column_placeholders = ', '.join('?' for _ in columns)
    table_name = table_dict['table_name']
    unique_col = table_dict['unique_column']

    sql_query = f"""
        INSERT INTO
            {table_name}({column_names})
        SELECT
            {column_placeholders}
        WHERE NOT EXISTS
            (SELECT 1 FROM {table_name} WHERE {unique_col}= ?)
        ;
    """

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
    with get_db_connection() as connection:

        for table in TABLES:
            upload_table_data(
                conn=connection, table_dict=table, df=clean_table[table['columns']])

        for table in FOREIGN_TABLES:
            if table['table_name'] == 'reading':
                upload_table_data_with_foreign_key(
                    conn=connection, table_dict=table, df=clean_table)
            else:
                upload_table_data_with_foreign_key(
                    conn=connection, table_dict=table, df=clean_table)
