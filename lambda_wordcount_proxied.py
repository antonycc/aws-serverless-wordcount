#!/usr/bin/env python3
# Purpose: Read a body and submit for a wordcount

import os
import logging
import json
import time
import uuid
import base64
import boto3
from pathlib import Path
import utils_authorization as auth
from http import HTTPStatus

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def lambda_handler(event, context):

    # Check Authorization
    api_secret = os.environ['ApiSecret']
    authorization_header = event['headers']['Authorization']
    current_time = int(time.time())
    if not auth.token_valid(authorization_header, api_secret):
        return {
            'statusCode': HTTPStatus.UNAUTHORIZED,
            'headers': {}
        }
    elif not auth.is_current(authorization_header, current_time):
        return {
            'statusCode': HTTPStatus.FORBIDDEN,
            'headers': {}
        }
    user = auth.get_user(authorization_header)
    expires = auth.get_expires(authorization_header)
    logger.info('Accepted bearer token for: {} (expires:{})'.format(user, expires))

    # Respond according to the HTTP verb
    if event['httpMethod'] == 'GET':
        return {
            'statusCode': HTTPStatus.OK,
            'headers': {}
        }
    elif event['httpMethod'] == 'POST':
        body = base64.b64decode(event['body'])
        filename = None
        # TODO: When filename argument is ommited this error occurs
        #   argument of type 'NoneType' is not iterable: TypeError
        #   Traceback (most recent call last):
        #   File "/var/task/lambda_wordcount_proxied.py", line 51, in lambda_handler
        #   if 'filename' in event['queryStringParameters']:
        #   TypeError: argument of type 'NoneType' is not iterable
        if 'queryStringParameters' in event:
            if 'filename' in event['queryStringParameters']:
                filename = event['queryStringParameters']['filename']
        upload_body(body, filename)
        return {
            'statusCode': HTTPStatus.ACCEPTED,
            'headers': {}
        }
    else:
        return {
            'statusCode': HTTPStatus.METHOD_NOT_ALLOWED,
            'headers': {}
        }

def upload_body(body, object_key=None):
    if object_key == None:
        object_key = '{}'.format(uuid.uuid4())
    tmp_file = Path('/tmp/{}'.format(uuid.uuid4()))
    open(str(tmp_file), 'wb').write(body)
    hopper_bucket = os.environ['HopperBucket']
    logger.info('Uploading {} to bucket {} using key {}'.format(str(tmp_file), hopper_bucket, object_key))
    s3_client.upload_file(str(tmp_file), hopper_bucket, object_key)

