import os
import pandas as pd
import boto3
import pymysql
from sqlalchemy import create_engine
import json

def get_rds_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

def read_csv_from_s3(bucket, key):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(obj['Body'])

def upload_to_rds(df, db_url, table_name):
    engine = create_engine(db_url)
    with engine.connect() as conn:
        df.to_sql(name=table_name, con=conn, index=False, if_exists='replace')
    print(f" Successfully uploaded to RDS: {table_name}")

def fallback_to_glue(s3_location, glue_db, glue_table, columns):
    glue = boto3.client('glue')
    try:
        glue.create_database(DatabaseInput={'Name': glue_db})
    except glue.exceptions.AlreadyExistsException:
        pass

    glue.create_table(
        DatabaseName=glue_db,
        TableInput={
            'Name': glue_table,
            'StorageDescriptor': {
                'Columns': [{'Name': col, 'Type': 'string'} for col in columns],
                'Location': s3_location,
                'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                'SerdeInfo': {
                    'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                    'Parameters': {'field.delim': ','}
                }
            },
            'TableType': 'EXTERNAL_TABLE'
        }
    )
    print(f"⚠️ Fallback activated. Glue Table created: {glue_table}")

def main():
    S3_BUCKET = os.getenv('S3_BUCKET')
    CSV_KEY = os.getenv('CSV_KEY')
    RDS_TABLE = os.getenv('RDS_TABLE')
    GLUE_DB = os.getenv('GLUE_DB')
    GLUE_TABLE = os.getenv('GLUE_TABLE')
    GLUE_LOCATION = os.getenv('GLUE_LOCATION')
    SECRET_NAME = os.getenv('SECRET_NAME', 'rds/mysql/prod')

    df = read_csv_from_s3(S3_BUCKET, CSV_KEY)

    try:
        secret = get_rds_secret(SECRET_NAME)
        db_url = f"mysql+pymysql://{secret['username']}:{secret['password']}@{secret['host']}:{secret.get('port', 3306)}/{secret['mydb']}"
        upload_to_rds(df, db_url, RDS_TABLE)
    except Exception as e:
        print(f" RDS Upload Failed: {e}")
        fallback_to_glue(GLUE_LOCATION, GLUE_DB, GLUE_TABLE, df.columns)

if __name__ == "__main__":
    main()

