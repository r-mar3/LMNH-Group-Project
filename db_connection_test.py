import pyodbc


def load_schema_file() -> str:
    with open('schema.sql', 'r') as f:
        schema_text = f.read()
    return schema_text


def get_db_connection() -> pyodbc.Connection:
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 18 for SQL Server}};'
        f'SERVER=c20-plants-db.c57vkec7dkkx.eu-west-2.rds.amazonaws.com, 1433;'
        f'DATABASE=plants;'
        f'UID=beta;'
        f'PWD=pswd-beta1;'
        f'TrustServerCertificate=yes;'
    )

    return conn


if __name__ == '__main__':
    conn = get_db_connection()
    cur = conn.cursor()
    schema_text = load_schema_file()

    commands = schema_text.split(';')
    for command in commands:
        print(command)
        cur.execute(command)

    print(cur.fetchone())
    cur.close()
    conn.close()
