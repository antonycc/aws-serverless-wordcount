#!/usr/bin/env python3
# Purpose: Object and string transformation tests

import uuid
import json
import logging
import boto3
from pathlib import Path
import utils_s3 as module_under_test

s3_client = boto3.client('s3')

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def test_get_s3_health():
    bucket = 'serverless-wordcount-archive'
    health = module_under_test.get_s3_health([bucket])
    logger.info('Health: {}'.format(json.dumps(health)))
    assert health['health_check_passed']

def test_get_s3_health_no_bucket():
    bucket = 'serverless-wordcount-archive-fake'
    health = module_under_test.get_s3_health([bucket])
    assert not health['health_check_passed']

def test_object_exists():
    bucket = 'serverless-wordcount-archive'
    object_key = 'ukpga_20100013_en.pdf-result.json'
    local_source_filepath = Path('./{}'.format(object_key))
    s3_client.upload_file(str(local_source_filepath), bucket, object_key)
    assert module_under_test.object_exists(bucket, object_key)

def test_object_exists_no_object():
    bucket = 'serverless-wordcount-archive'
    object_key = '{}'.format(uuid.uuid4())
    assert not module_under_test.object_exists(bucket, object_key)

def test_read_object_to_json():
    logger.info("PASS::test_read_object_to_json")
    bucket = 'serverless-wordcount-archive'
    object_key = 'ukpga_20100013_en.pdf-result.json'
    tmp_path = Path('.')
    local_source_filepath = Path('./{}'.format(object_key))
    s3_client.upload_file(str(local_source_filepath), bucket, object_key)
    json_object = module_under_test.read_object_to_json(tmp_path, bucket, object_key)
    assert len(json_object) > 0

#def test_body_to_local():
#    #body_to_local(body)
#    logger.info("PASS::test_body_to_local")

#def test_body_to_s3():
#    #body_to_local(body)
#    logger.info("PASS::test_body_to_s3")

