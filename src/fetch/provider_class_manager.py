from .provider.EIA.eia_data_fetcher import EIADataFetcher
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class ProviderClassManager:
    def __init__(self, config_path: str):
        """
        Initializes the ProviderClassManager with available data providers and configuration file
        """
        self.config_path = config_path
        self.providers = {
            "EIA": EIADataFetcher
        }

        if not self.config_path:
            raise ValueError("Invalid config path: %s", self.config_path)

        logger.info("ProviderClassManager initialized with config path: %s", self.config_path)

    def fetch_data(self, provider_name: str):
        """
        Fetches data from the specified provider.

        Args:
            provider_name (str): The name of the provider to fetch data from

        Returns:
            DataFrame: The fetched data as a DataFrame

        Raises:
            ValueError: If the specified provider name does not have an associated data fetcher class
        """
        logger.debug("Fetching data from provider: %s", provider_name)
        provider_class = self.providers.get(provider_name)
        if provider_class is None:
            raise ValueError(f"No provider class found for {provider_name}")
        try:
            return provider_class(self.config_path).fetch_data()
        except Exception as e:
            logger.error("Failed to fetch data from %s: %s", provider_name, e)
            raise