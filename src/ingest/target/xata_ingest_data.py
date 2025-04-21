import psycopg2
import pandas as pd
import json
import os
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from logger import Logger

logger = Logger().get_logger()

class XataIngest:
    def __init__(self, config_path, df):
        """Initializes the XataIngest with the configuration and data to ingest.

        Args:
            config_path (str): The path to the JSON configuration file.
            df (pd.DataFrame): The DataFrame containing data to be ingested.
        """
        load_dotenv()
        self.df = df

        with open(config_path, 'r') as file:
            config = json.load(file)

        self.target = config['ingest']['target']
        self.table_name = config['ingest']['table_name']
        self.dsn = os.getenv("DSN")

    def ingest_data(self) -> None:
        """Ingests data into the specified database table."""
        try:
            cnn = psycopg2.connect(self.dsn)
            cur = cnn.cursor()

            records = self.df.to_dict(orient='records')
            insert_query = (
                f"INSERT INTO {self.table_name} ({', '.join(records[0].keys())}) VALUES %s"
            )
            values = [tuple(record.values()) for record in records]

            cur.execute('BEGIN;')
            execute_values(cur, insert_query, values, page_size=1000)
            cnn.commit()
            logger.info(f"Inserted {len(records)} records into {self.table_name}.")
        except Exception as e:
            logger.error(f"Error inserting records: {e}")
            cnn.rollback()
        finally:
            cur.close()
            cnn.close()
