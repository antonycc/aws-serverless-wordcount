#!/usr/bin/env python3
# Purpose: Read a body and submit for a wordcount

import os
import logging
import json
import time
import base64
import boto3
from pathlib import Path
import utils_authorization as auth

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    api_secret = os.environ['ApiSecret']
    authorization_header = event['headers']['Authorization']
    current_time = time.time()
    if not auth.token_valid(authorization_header, api_secret):
        return {
            "statusCode": 401,
            "headers": {}
        }
    else if not auth.is_current(authorization_header, current_time):
        return {
            "statusCode": 403,
            "headers": {}
        }
    else if event['httpMethod'] == "GET":
        return {
            "statusCode": 200,
            "headers": {}
        }
    else if event['httpMethod'] == "POST":
        # TODO if filename in query parameter
        # TODO     object_key = filename in query parameter
        # TODO  else:
        object_key = uuid.uuid4()
        tmp_file = Path('/tmp/{}'.format(uuid.uuid4()))
        body_bytes = base64.b64decode(event['body'])
        open(str(tmp_file), 'wb').write(body_bytes)
        hopper_bucket = os.environ['HopperBucket']
        s3_client.upload_file(str(tmp_file), hopper_bucket, object_key)
        return {
            "statusCode": 202,
            "headers": {}
        }
    else:
        return {
            "statusCode": 405,
            "headers": {}
        }
