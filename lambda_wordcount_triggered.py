#!/usr/bin/env python3
# Purpose: Handle the AWS native elements then hand off a wordcount

import os
import logging
import uuid
import boto3
import task_wordcount as task
from pathlib import Path
from hashlib import sha256

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
    local_source_filepath = Path('{}/{}'.format(tmp_path, object_key))
    s3_client.download_file(hopper_bucket, object_key, str(local_source_filepath))

    filename_prefix = "{}".format(sha256(object_key.encode("utf-8")).hexdigest())
    local_descriptor_filename = "{}-descriptor.json".format(filename_prefix)
    local_descriptor_filepath = Path('{}/{}'.format(tmp_path, local_descriptor_filename))
    local_result_filename = "{}-wordcount.json".format(filename_prefix)
    local_result_filepath = Path('{}/{}'.format(tmp_path, local_result_filename))
    task.do_task(tmp_path,
        str(local_source_filepath),
        str(local_descriptor_filepath),
        str(local_result_filepath))

    result_key = '{}{}'.format(object_key, result_postfix)
    s3_client.upload_file(str(local_result_filepath), result_bucket, result_key)
    logger.info('Created s3://{}/{}'.format(result_bucket, object_key))
    descriptor_key = '{}{}{}'.format(object_key, result_postfix, '.descriptor.json')
    s3_client.upload_file(str(local_descriptor_filepath), result_bucket, descriptor_key)

    s3_client.upload_file(str(local_source_filepath), archive_bucket, object_key)
    s3_client.delete_object(Bucket=hopper_bucket, Key=object_key)
    logger.info('Created s3://{}/{}'.format(archive_bucket, object_key))
