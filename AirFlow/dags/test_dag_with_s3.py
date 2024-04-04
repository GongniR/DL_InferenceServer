import pendulum
import requests
from typing import List
import json

from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

@dag(
    'test',
    schedule=None,
    start_date=pendulum.datetime(2023, 4, 4, tz="UTC"),
    catchup=False,
    tags=["JOJO"],
)
def my_very_own_etl():

    @task()
    def extract() -> List[dict]:
        request = requests.get("https://api.thecatapi.com/v1/images/search?limit=10")
        request.raise_for_status()
        return request.json()

    @task()
    def transform(data: List[dict]) -> List[str]:
        return [i['url'] for i in data]

    @task()
    def load(data: List[str]):
        hook = S3Hook(aws_conn_id="S3_ETL_CONN")
        extra = hook.get_connection(hook.aws_conn_id).get_extra()
        bucket_name = json.loads(extra).get('bucket_name')
        if bucket_name:
            for url in data:
                r = requests.get(url)
                r.raise_for_status()
                hook.load_bytes(r.content, key=url.split('/')[-1], bucket_name=bucket_name)
        else:
            raise ValueError("Bucket name not found in connection extra")

    extracted_data = extract()
    transformed_data = transform(extracted_data)
    load(transformed_data)

my_very_own_etl_dag = my_very_own_etl()