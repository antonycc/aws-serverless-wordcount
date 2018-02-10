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
    if health['health_check_passed']:
        logger.info("PASS::test_get_s3_health")
    else:
        logger.error("FAIL::test_get_s3_health")
        exit(1)

def test_get_s3_health_no_bucket():
    bucket = 'serverless-wordcount-archive-fake'
    health = module_under_test.get_s3_health([bucket])
    if not health['health_check_passed']:
        logger.info("PASS::test_get_s3_health")
    else:
        logger.error("FAIL::test_get_s3_health")
        exit(1)

def test_object_exists():
    bucket = 'serverless-wordcount-archive'
    object_key = 'ukpga_20100013_en.pdf-result.json'
    local_source_filepath = Path('./{}'.format(object_key))
    s3_client.upload_file(str(local_source_filepath), bucket, object_key)
    if module_under_test.object_exists(bucket, object_key):
        logger.info("PASS::test_object_exists")
    else:
        logger.error("FAIL::test_object_exists")
        exit(1)

def test_object_exists_no_object():
    bucket = 'serverless-wordcount-archive'
    object_key = '{}'.format(uuid.uuid4())
    if not module_under_test.object_exists(bucket, object_key):
        logger.info("PASS::test_object_exists")
    else:
        logger.error("FAIL::test_object_exists")
        exit(1)

def test_read_object_to_json():
    logger.info("PASS::test_read_object_to_json")
    bucket = 'serverless-wordcount-archive'
    object_key = 'ukpga_20100013_en.pdf-result.json'
    local_source_filepath = Path('./{}'.format(object_key))
    s3_client.upload_file(str(local_source_filepath), bucket, object_key)
    json_object = module_under_test.read_object_to_json(bucket, object_key)
    if len(json_object) > 0:
        logger.info("PASS::test_read_object_to_json")
    else:
        logger.error("FAIL::test_read_object_to_json")
        exit(1)

#def test_body_to_local():
#    #body_to_local(body)
#    logger.info("PASS::test_body_to_local")

#def test_body_to_s3():
#    #body_to_local(body)
#    logger.info("PASS::test_body_to_s3")

def run_tests():
    test_get_s3_health()
    test_get_s3_health_no_bucket()
    test_object_exists()
    test_read_object_to_json()
#    test_body_to_local()
#    test_body_to_s3()

run_tests()
