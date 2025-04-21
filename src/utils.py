import json
import os
from dotenv import load_dotenv
from logger import Logger 

load_dotenv()

logger = Logger().get_logger()

class ConfigParamsLoader:
    def __init__(self, config_path):
        """Initializes the ConfigParamsLoader with the path to the config file.

        Args:
            config_path (str): The path to the JSON configuration file.
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        """Load JSON config file.

        Returns:
            dict: The contents of the JSON config file.
        """
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            raise

    def get_provider_name(self):
        """Get the provider name from the configuration.

        Returns:
            str: The provider name specified in the config.
        """
        return self.config['providers']['provider']

    def get_target(self):
        """Get the target for data ingestion from the configuration.

        Returns:
            str: The target specified in the config for data ingestion.
        """
        return self.config['ingest']['target']


class LoadRule:
    def __init__(self, config_path):
        """Initializes the LoadRule with the path to the config file.

        Args:
            config_path (str): The path to the JSON configuration file.
        """
        self.config_path = config_path

    def _load_config(self):
        """Load JSON config file.

        Returns:
            dict: The contents of the JSON configuration file.
        """
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            raise

    def load_symbol_replacement(self):
        """Load the symbol replacement rules from the configuration.

        Returns:
            dict: The symbol replacement rules specified in the config.
        """
        config = self._load_config()
        return config['rules']['symbol_replacement']

    def load_null_value_replacement(self):
        """Load the null value replacement rules from the configuration.

        Returns:
            dict: The null value replacement rules specified in the config.
        """
        config = self._load_config()
        return config['rules']['null_value_replacement']


class DataPreprocessor:
    def __init__(self, symbol_replacement, null_value_replacement):
        """Initializes the DataPreprocessor with symbol and null value replacements.

        Args:
            symbol_replacement (dict): A dictionary containing symbol replacement rules.
            null_value_replacement (dict): A dictionary containing null value replacement rules.
        """
        self.symbol_replacement = symbol_replacement
        self.null_value_replacement = null_value_replacement

    def replace_symbols(self, df):
        """Replace specified symbols in the DataFrame column headers.

        Args:
            df (pd.DataFrame): The DataFrame whose column headers will be modified.

        Returns:
            pd.DataFrame: The DataFrame with modified column headers.
        """
        title_row = df.columns
        for replacement in self.symbol_replacement["replacements"]:
            for symbol in replacement["symbols"]:
                title_row = title_row.str.replace(symbol, replacement["replace_with"], regex=True)
        df.columns = title_row
        logger.info(f"Replaced symbols in column headers: {self.symbol_replacement['replacements']}")
        return df

    def replace_null(self, df):
        """Replace null values in the DataFrame with specified values.

        Args:
            df (pd.DataFrame): The DataFrame in which null values will be replaced.

        Returns:
            pd.DataFrame: The DataFrame with null values replaced.
        """
        df.fillna(self.null_value_replacement["replace_with"], inplace=True)
        logger.info(f"Replaced null values with: {self.null_value_replacement['replace_with']}")
        return df