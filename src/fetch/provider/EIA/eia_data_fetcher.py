from typing import Protocol
import pandas as pd
import requests
import json
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class ProviderProtocol(Protocol):
    def fetch_data(self) -> pd.DataFrame:
        """Method to fetch data from the provider."""
        ...

class EIADataFetcher:
    def __init__(self, config_path):
        """
        Initializes the EIADataFetcher with necessary parameters.

        Attributes:
        config_path: (str) json file path
        """
        logger.info("Intializing EIA Data Fetcher with config path: %s", config_path)
        try:
            with open(config_path, 'r') as file:
                config = json.load(file)
            load_dotenv()
            self.base_url = config['providers']['base_url']
            self.data = config['providers']['params']['data']
            self.frequency = config['providers']['params']['frequency']
            self.sort = config['providers']['params']['sort']
            self.facets = config['providers']['params']['facets']
            self.api_key = os.getenv('EIA_API_KEY')
            self.start = config['providers']['params']['start']
            self.end = config['providers']['params']['end']
            self.length = config['providers']['length']
            self.offset = config['providers']['offset']
        except Exception as e:
            logger.error("Error initializing EIA Data Fetcher: %s", e)
            raise

    def build_query_params(self) -> str:
        """
        Build the query parameters for the API request.

        Returns:
            dict: A dictionary of query parameters.
        """
        logging.debug("Building Query Parameters")
        query_params = {
            "api_key": self.api_key,
            "frequency": self.frequency,
            "start": self.start,
            "end": self.end,
            "offset": self.offset,  
            "length": self.length
        }

        # Add data fields to query parameters
        for idx, data_field in enumerate(self.data):
            query_params[f"data[{idx}]"] = data_field

        # Add facets to query parameters
        for key, values in self.facets.items():
            for i, value in enumerate(values):
                query_params[f"facets[{key}][{i}]"] = value

        # Add sorting parameters to query parameters
        for idx, sort_param in enumerate(self.sort):
            query_params[f"sort[{idx}][column]"] = sort_param["column"]
            query_params[f"sort[{idx}][direction]"] = sort_param["direction"]

        logger.debug("Query params built : %s", query_params)
        return query_params

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch data from the EIA API, handling pagination as necessary

        Returns:
            pd.DataFrame: A DataFrame containing all fetched data

        Raises:
            Exception: If the response is not successful or the data format is unexpected
        """
        all_data = pd.DataFrame()  # Initialize an empty DataFrame for accumulated data
        logger.info("Fetching Data from EIA API")
        while True:
            # Build the query parameters for the API request
            query_params = self.build_query_params() 
            # Send a GET request to the API with the query parameters
            response = requests.get(self.base_url, params=query_params)

             # Check if the response status is OK
            if response.status_code == 200:
                # Parse the JSON response data
                data = response.json()
                # Verify that the expected keys are in the response
                if 'response' in data and 'data' in data['response']:
                    batch_data = data['response']['data'] # Extract the batch of data
                    # Check if there is no data in the current batch
                    if not batch_data: 
                        print("No more data available.")
                        break # Exit the loop if there's no more data
                    # Normalize the batch data into a DataFrame
                    fetched_df = pd.json_normalize(batch_data)
                    # Concatenate the newly fetched DataFrame with the accumulated DataFrame
                    all_data = pd.concat([all_data, fetched_df], ignore_index=True)
                    logger.info("Fetched %d records with offset %d.", len(batch_data), self.offset)
                    self.offset += self.length # Update the offset for the next request
                    # If the number of records fetched is less than the requested length, stop fetching
                    if len(batch_data) < self.length:
                        logger.info("Fetched less than requested length. Stopping fetch.")
                        break
                else:
                    # Raise an exception if the data format is not as expected
                    raise Exception("Unexpected data format in response")
            else:
                # Raise an exception if the API request fails
                raise Exception(f"Failed to fetch data: {response.status_code}, Response: {response.text}")

        logger.info("Data fetch completed!")
        return all_data 