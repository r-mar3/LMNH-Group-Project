"""Extracts all data from the RDS to be displayed on the dashboard"""
import pyodbc
from dotenv import load_dotenv
from os import environ
import pandas as pd


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


def get_all_data() -> pd.DataFrame:
    conn = get_db_connection()
    query = """
            SELECT *
            FROM reading r
            JOIN botanist b ON r.botanist_id = b.botanist_id
            JOIN plant p ON p.plant_id = r.plant_id
            JOIN origin o ON o.origin_id = p.origin_id
            JOIN species s ON s.species_id = p.species_id
            JOIN city ci ON ci.city_id = o.city_id
            JOIN country co ON co.country_id = ci.country_id
            """

    data = pd.read_sql_query(query, conn)

    return data


if __name__ == "__main__":
    get_all_data()
