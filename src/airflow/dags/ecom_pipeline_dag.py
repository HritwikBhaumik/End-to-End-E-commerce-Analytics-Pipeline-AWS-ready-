from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os, subprocess, boto3, glob, pandas as pd
from sqlalchemy import create_engine
DEFAULT_ARGS={'owner':'airflow','depends_on_past':False,'email_on_failure':False,'retries':1,'retry_delay':timedelta(minutes=5)}
DAG_ID='ecom_pipeline'
def generate(**context): subprocess.check_call(['python','/opt/airflow/dags/../data_gen/generate_orders.py','--out','/opt/airflow/data/bronze','--num','200'])
def upload(**context):
    session=boto3.session.Session(); s3=session.client('s3'); local_dir='/opt/airflow/data/bronze'; bucket=os.environ.get('BUCKET_NAME'); prefix='bronze/orders'
    for root,_,files in os.walk(local_dir):
        for fn in files:
            s3.upload_file(os.path.join(root,fn),bucket,f"{prefix}/{fn}")
def run_glue_or_spark(**context):
    spark_script='/opt/airflow/dags/../glue/glue_etl.py'; input_path=os.environ.get('BRONZE_PATH','/opt/airflow/data/bronze'); silver_path=os.environ.get('SILVER_PATH','/opt/airflow/data/silver'); gold_path=os.environ.get('GOLD_PATH','/opt/airflow/data/gold')
    subprocess.check_call(['spark-submit',spark_script,'--input',input_path,'--silver',silver_path,'--gold',gold_path])
def load_to_redshift(**context):
    pg_url=f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}/{os.environ.get('POSTGRES_DB')}"
    engine=create_engine(pg_url); files=glob.glob('/opt/airflow/data/gold/*/*.parquet'); frames=[]
    for p in files: frames.append(pd.read_parquet(p))
    if frames: pd.concat(frames,ignore_index=True).to_sql('sales_daily',engine,if_exists='replace',index=False)
with DAG(DAG_ID, default_args=DEFAULT_ARGS, schedule_interval='@daily', start_date=datetime(2025,1,1), catchup=False) as dag:
    t1=PythonOperator(task_id='generate_data',python_callable=generate)
    t2=PythonOperator(task_id='upload_to_s3',python_callable=upload)
    t3=PythonOperator(task_id='run_spark',python_callable=run_glue_or_spark)
    t4=PythonOperator(task_id='load_to_redshift',python_callable=load_to_redshift)
    t1>>t2>>t3>>t4
