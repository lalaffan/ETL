from .target.xata_ingest_data import XataIngest
import pandas as pd
from logger import Logger


logger = Logger().get_logger()

class IngestClassManager:
    def __init__(self, config_path: str):
        """Initializes the IngestClassManager with a configuration path.

        Args:
            config_path (str): The path to the JSON configuration file.
        """
        self.config_path = config_path
        self.ingesters = {'Xata': XataIngest}

    def ingest_data(self, df: pd.DataFrame, target: str):
        """Ingests data using the specified target.

        Args:
            df (pd.DataFrame): The DataFrame containing data to be ingested.
            target (str): The target for data ingestion.

        Raises:
            Exception: If the target ingester class does not exist.
        """
        ingester_class = self.ingesters.get(target)
        if ingester_class is None:
            logger.error(f"No such ingester class exists for {target}")
            raise Exception(f"No such ingester class exists for {target}")

        ingester_instance = ingester_class(self.config_path, df)
        return ingester_instance.ingest_data()
