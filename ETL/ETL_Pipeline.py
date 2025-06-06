from ETL.extract import extract_from_mongodb
from ETL.transform import transform_data
from ETL.load import create_tables_and_Load_data
from dotenv import load_dotenv
import os

def main():
    # Step 1: Load environment variables
    load_dotenv()

    # Step 2: Extract raw data from MongoDB
    print(" Extracting data from MongoDB...")
    raw_data = extract_from_mongodb()
    if raw_data is None:
        print(" Extraction failed. Stopping the pipeline.")
        return

    # Step 3: Transform raw data
    print(" Transforming extracted data...")
    transformed_data = transform_data(raw_data)

    # step 4: Load transformed data into PostgreSQL
    print(" Loading transformed data into PostgreSQL...")
    create_tables_and_Load_data(transformed_data)
    print(" ETL pipeline completed successfully.")

if __name__ == "__main__":
    main()
      