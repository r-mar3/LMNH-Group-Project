import pyodbc
from os import environ
from dotenv import load_dotenv
import pandas as pd


def get_db_connection() -> pyodbc.Connection:
    """Returns a live connection to the database"""
    load_dotenv()
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 18 for SQL Server}};'
        f'SERVER={environ['DB_HOST']}, {environ['DB_PORT']};'
        f'DATABASE={environ['DB_NAME']};'
        f'UID={environ['DB_USER']};'
        f'PWD={environ['DB_PASSWORD']};'
        f'TrustServerCertificate=yes;'
    )

    return conn


def load_csv(filepath: str) -> pd.DataFrame:
    """Returns a dataframe of the csv at a given filepath"""
    return pd.read_csv(filepath)


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
    print(sql_query)

    cur = conn.cursor()
    cur.executemany(sql_query, [tuple(row) for row in df.to_numpy()])
    print("ROWCOUNT:", cur.rowcount)
    cur.close()


if __name__ == '__main__':
    with get_db_connection() as conn:
        table_name = 'country'
        country_df = load_csv(f'{table_name}.csv')
        upload_table_data(conn, table_name, country_df)
