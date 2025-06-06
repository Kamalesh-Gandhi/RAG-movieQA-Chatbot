from sqlalchemy import create_engine, inspect, text
import os
from ETL.db_schema import metadata
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")   
port = os.getenv("POSTGRES_PORT")
db_name = os.getenv("POSTGRES_DB")
db_uri = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(db_uri)
inspector = inspect(engine)

def create_tables_and_Load_data(transformed_data:dict):
    """
    creating table and Loads the transformed data into PostgreSQL database.
    
    Args:
        dataframe (dict): Dictionary containing DataFrames to be loaded.
        
    Returns:
        None
    """
    print("Dropping existing tables if they exist...")
    metadata.drop_all(engine)
    print("Existing tables dropped successfully.")

    print("Creating Tables....")
    metadata.create_all(engine)
    print("Tables created successfully.")

    def clear_table_if_exists(table_name):
        """
        Clears the specified table if it exists in the PostgreSQL database.
        
        Args:
            table_name (str): Name of the table to be cleared.
            
        Returns:
            None
        """
        if table_name in inspector.get_table_names():
            with engine.begin() as conn:
                print(f"Clearing table {table_name}...")
                conn.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
        else:
            print(f"Table {table_name} does not exist. Skipping clear operation.")
    

    def load_data_to_postgres(table_name, dataframe):
        """
        Loads a DataFrame into the specified PostgreSQL table.
        
        Args:
            table_name (str): Name of the table to load data into.
            dataframe (pd.DataFrame): DataFrame containing data to be loaded.
            
        Returns:
            None
        """
        try:
            clear_table_if_exists(table_name)
            print(f"Loading data into {table_name}...")
            dataframe.to_sql(table_name, con=engine, if_exists='append', index=False)
            print(f"loaded {len(dataframe)} rows into {table_name} successfully.")
        except Exception as e:
            print(f"An error occurred while loading data into {table_name}: {str(e)}")

    
    load_data_to_postgres("movies", transformed_data["movies"])
    load_data_to_postgres("users", transformed_data["users"])
    load_data_to_postgres("comments", transformed_data["comments"])
    load_data_to_postgres("theaters", transformed_data["theaters"])
    load_data_to_postgres("sessions", transformed_data["sessions"])
    print("Data loaded successfully into PostgreSQL database.")

