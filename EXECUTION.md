### Execution of Project

This project allows fetching data from different providers, preprocessing it, and ingesting it in the target system. Below are steps to execute the project:

Step 1:
<br /> Setup the Environment:
* Clone the repository and install all required dependencies
* Create .env file

Step 2:
<br /> Configure Provider and Target
* Upload your json file in configs folder
* If working with a Provider or Target not present:
    * Create corresponding class provider.py or ingest.py following the name convention as:
        * For Provider: Create a class named {ProviderName}DataFetcher in fetch/provider/provider_name/provider_name_data_fetcher.py 
        * For Target: Create a class named {Target}Ingest in ingest/target/target_name/target_name_data_ingester.py

Step 3:
<br /> Fetching Data, Preprocessing it and Ingesting it
* Run main.py in order to execute the pipeline

Note: 
* While creating new provider add the provider and ingester module in manager file and add corresponding class name in the Map
* Ensure class has a method fetch_data() when creating provider class and ingest_data() while creating target class