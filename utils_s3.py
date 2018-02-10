#!/usr/bin/env python3
# Purpose: S3 utilities wrapping boto2

import logging
import json
import uuid
import boto3
from pathlib import Path

s3_client = boto3.client('s3')

logger = logging.getLogger()

def get_s3_health(buckets):
    s3_health = {}
    health_check_passed = True
    for bucket in buckets:
        bucket_health = get_bucket_health(bucket)
        s3_health[bucket] = bucket_health
        health_check_passed = health_check_passed and (bucket_health == 'ok')
    s3_health['health_check_passed'] = health_check_passed
    return s3_health

def get_bucket_health(bucket):
    try:
        s3_objects = s3_client.list_objects_v2(Bucket=bucket, MaxKeys=0)
        if s3_objects['ResponseMetadata']['HTTPStatusCode'] == 200:
            return 'ok'
        else:
            return s3_objects
    except Exception as e:
        logger.error("Error {} Could not execute list_objects_v2: [{}]".format(str(e), bucket), exc_info=True) 
        return e

def object_exists(bucket, object_key):
    s3_objects = s3_client.list_objects_v2(Bucket=bucket)
    logger.debug('Bucket {}:'.format(bucket))
    logger.debug('{}'.format(s3_objects))
    #logger.debug(json.dumps(s3_objects))
    if 'Contents' in s3_objects:
        for candidate_result in s3_objects['Contents']:
            if candidate_result['Key'] == object_key:
                logger.info('Resource Exists s3://{}/{}'.format(bucket, object_key))
                return True
    logger.info('Did not find s3://{}/{}'.format(bucket, object_key))
    return False

def read_object_to_json(tmp_path, bucket, object_key):
    local_result_filepath = Path('{}/{}'.format(str(tmp_path), uuid.uuid4()))
    s3_client.download_file(bucket, object_key, str(local_result_filepath))
    result_string = local_result_filepath.read_text()
    result = json.loads(result_string)
    return result

def body_to_local(tmp_path, body):
    logger.info('Synchronous processing...')
    local_source_filepath = Path('{}/{}'.format(str(tmp_path), uuid.uuid4()))
    open(str(local_source_filepath), 'wb').write(body)
    return local_source_filepath
    
def body_to_s3(tmp_path, body, bucket, object_key=None):
    logger.info('Asynchronous processing...')
    if object_key == None:
        object_key = '{}.pdf'.format(uuid.uuid4())
    tmp_file = Path('{}/{}'.format(str(tmp_path), uuid.uuid4()))
    open(str(tmp_file), 'wb').write(body)
    logger.info('Uploading {} to bucket {} using key {}'.format(str(tmp_file), bucket, object_key))
    s3_client.upload_file(str(tmp_file), bucket, object_key)
    return object_key
