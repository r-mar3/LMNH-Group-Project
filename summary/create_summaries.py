# pylint: disable=c-extension-no-member
"""Generates and uploads summary data for plant readings from the past day"""
from os import environ
from datetime import datetime
import io
from dotenv import load_dotenv
import pandas as pd
import pyodbc
import boto3


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


def upload_df_to_s3(df: pd.DataFrame) -> None:
    """Takes a dataframe and uploads it to the S3 bucket"""
    filename = f'{datetime.today().date()}.csv'
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    load_dotenv()
    session = boto3.Session(aws_access_key_id=environ["ACCESS_KEY"],
                            aws_secret_access_key=environ["SECRET_ACCESS_KEY"],
                            region_name=environ["REGION"])
    s3_bucket_name = environ["BUCKET_NAME"]

    s3_client = session.resource('s3')
    s3_client.Object(s3_bucket_name, filename).put(Body=csv_buffer.getvalue())


def get_reading_data(conn: pyodbc.Connection) -> pd.DataFrame:
    """Fetches the reading data for the past day from the database"""
    sql_query = """
        SELECT *
        FROM reading
        WHERE reading_time_taken >= DATEADD(day, -1, GETDATE());
    """

    cur = conn.cursor()
    cur.execute(sql_query)
    columns = [column[0] for column in cur.description]
    readings_df = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
    cur.close()

    return readings_df


def generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Takes a reading table and creates summary data"""
    summary_df = (
        df.groupby('plant_id')
        .agg({
            'reading_temperature': 'mean',
            'reading_soil_moisture': 'mean',
            'reading_error': 'sum',
            'reading_alert': 'sum'
        })
        .reset_index()
    )

    return summary_df


if __name__ == '__main__':
    with get_db_connection() as connection:
        reading_data = get_reading_data(connection)
        summary_data = generate_summary(reading_data)
        upload_df_to_s3(summary_data)
