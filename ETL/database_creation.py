from sqlalchemy import create_engine, text
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_postgres_db():
    """
    Creates a PostgreSQL database using the connection string from environment variables.
    """
    
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db_name = os.getenv("POSTGRES_DB")      

    try:
        conn = psycopg2.connect(
            dbname = 'postgres',  # Connect to the default database
            user = user,
            password = password,
            host = host,
            port = port
        )

        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()

        if not exists:
            print(f"Database '{db_name}' does not exist. Creating it...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' already exists.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"An error occurred while creating the database: {str(e)}")


if __name__ == "__main__":
    create_postgres_db()
    print("PostgreSQL database creation script executed successfully.")