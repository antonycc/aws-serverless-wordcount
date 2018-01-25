#!/usr/bin/env python3
# Purpose: Handle the AWS native elements then hand off a word count

import os
import logging
import uuid
import boto3
import task_wordcount as task
from pathlib import Path

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def lambda_handler(event, context):    
    if 'Records' in event:
        process_all_records(event['Records'])

def process_all_records(records):
    logger.info('Processing all records...')
    result_bucket = os.environ['ResultBucket']
    result_postfix = os.environ['ResultPostfix']
    archive_bucket = os.environ['ArchiveBucket']
    tmp_path = Path('/tmp')
    for record in records:
        hopper_bucket = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key'] 
        process_record(str(tmp_path), hopper_bucket, object_key, result_bucket, result_postfix, archive_bucket)

def process_record(tmp_path, hopper_bucket, object_key, result_bucket, result_postfix, archive_bucket):
    local_source_filepath = '{}/{}'.format(tmp_path, uuid.uuid4())
    s3_client.download_file(hopper_bucket, object_key, local_source_filepath)

    local_result_filepath = '{}/{}'.format(tmp_path, uuid.uuid4())
    task.do_task(tmp_path, local_source_filepath, local_result_filepath)
    
    result_key = '{}{}'.format(object_key, result_postfix)
    s3_client.upload_file(local_result_filepath, result_bucket, result_key)
    logger.info('Created s3://{}/{}'.format(result_bucket, object_key))
    
    s3_client.upload_file(local_source_filepath, archive_bucket, object_key)
    s3_client.delete_object(hopper_bucket, object_key)
    logger.info('Created s3://{}/{}'.format(archive_bucket, object_key))
