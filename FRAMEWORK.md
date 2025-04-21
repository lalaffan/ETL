### Framework of the Project

#### Configuration
The configuration consists of a JSON file which maily includes parameters associated with the provider and the ingest.

![Initailization and Configuration](https://github.com/mentorship-guidance/fire_group_energy_efficiency_etl/blob/manali/images/init_config.png)

#### Data Fetch Layer
Dynamically instantiate the appropiate data fetcher based on the provider name present in the config. For current case we have a Class that fetches data from EIA website. 

![Data Fetch Layer](https://github.com/mentorship-guidance/fire_group_energy_efficiency_etl/blob/manali/images/data_fetch.png)

#### Process Dataframe
Process the data before ingesting it into a database. Basic processing includes converting '-' to '_', identifying data type, filling null values.

#### Data Ingest Layer
Dynamically instantiate the appropiate data ingester based on the ingest name present in the config. For current case we have a Class that ingests data to Xata Client.

![Data Ingest Layer](https://github.com/mentorship-guidance/fire_group_energy_efficiency_etl/blob/manali/images/data_ingest.png)

#### Main Pipeline Logic
Load Fetcher and Ingester classes for using objects of the classes developed. 

![Main Pipeline Logic](https://github.com/mentorship-guidance/fire_group_energy_efficiency_etl/blob/manali/images/main_pipeline.png)

#### Environment
Store important database credentials and API keys