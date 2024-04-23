from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.sensors.s3_key_sensor import S3KeySensor
from airflow.hooks.S3_hook import S3Hook
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 23),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta( minutes=5),
}



dag = DAG(
    's3_bucket_check_and_download',
    default_args=default_args,
    description='DAG to check for files in S3 bucket and download all files',
    schedule_interval=timedelta(days=1),
)

start_task = DummyOperator(task_id='start', dag=dag)
end_task = DummyOperator(task_id='end', dag=dag)

# Define a function to download files from S3
def download_files_from_s3(**kwargs):
    s3_hook = S3Hook(aws_conn_id='aws_default')
    s3_bucket = kwargs['dag_run'].conf.get('s3_bucket')

    # Get list of files in S3 bucket
    files = s3_hook.list_keys(bucket_name=s3_bucket)

    print(files)
    # Download each file
    for file in files:
        s3_hook.download_file(bucket_name=s3_bucket, key=file, local_path='/home/auser/DL_InferenceServer' + os.path.basename(file))

download_task = PythonOperator(
    task_id='download_files_from_s3',
    python_callable=download_files_from_s3,
    provide_context=True,
    dag=dag,
)

check_s3_bucket_sensor = S3KeySensor(
    task_id='check_s3_nii_file',
    bucket_key = "18h.gif",
    bucket_name='niftytest',  # Specify your S3 bucket name
    timeout=18 * 60 * 60,  # Timeout in seconds (18 hours)
    poke_interval=10,  # Check interval in seconds
    aws_conn_id='S3_ETL_CONN',  # Connection ID to AWS
    dag=dag,
)


start_task >> check_s3_bucket_sensor >> download_task >> end_task