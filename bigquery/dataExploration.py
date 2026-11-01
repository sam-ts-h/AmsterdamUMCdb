import os

import pandas as pd
from google.cloud import bigquery

#login terminal commadns
#brew install --cask google-cloud-sdk   # skip if already installedd
#gcloud auth application-default login
#gcloud auth application-default set-quota-project liquid-folio-513114-d9

projectId = "liquid-folio-513114-d9"
datasetId = "amsterdamumcdb.version1_5_0"
location = "eu"

os.environ["GOOGLE_CLOUD_PROJECT"] = projectId
pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 200)

#default dataset
jobConfig = bigquery.QueryJobConfig(default_dataset=datasetId)
client = bigquery.Client(project=projectId, location=location, default_query_job_config=jobConfig)

person = client.query("SELECT * FROM person").to_dataframe()
print(f"Number of persons: {len(person)}")
print(person.head(10))
