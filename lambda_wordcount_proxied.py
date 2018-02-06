#!/usr/bin/env python3
# Purpose: Read a body and submit for a wordcount

import os
import logging
import json
import time
import uuid
import base64
import boto3
from http import HTTPStatus
from pathlib import Path
import utils_authorization as auth
import task_wordcount as task

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

s3_client = boto3.client('s3')

def lambda_handler(request, context):
    logger.debug('REQUEST:')
    logger.debug(request)
    api_secret = os.environ['ApiSecret']
    authorization_header = request['headers']['Authorization']
    current_time = int(time.time())
    response = web_handler(request, authorization_header, api_secret, current_time)
    logger.debug('RESPONSE:')
    logger.debug(response)
    return response

def web_handler(event, authorization_header, api_secret, current_time):

    # Check Authorization
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
        qparams = get_query_string_parameters(event)
        if qparams['is_synchronous']:
            return process_body(body)
        else:
            return upload_body(body, qparams['filename'])
    else:
        return {
            'statusCode': HTTPStatus.METHOD_NOT_ALLOWED,
            'headers': {}
        }

def get_query_string_parameters(request):
    qparams = {
        'filename': None,
        'is_synchronous': False    
    }
    filename = None
    is_synchronous = False
    if ('queryStringParameters' in request) and request['queryStringParameters']:
        if 'filename' in request['queryStringParameters']:
            qparams['filename'] = request['queryStringParameters']['filename']
        qparams['is_synchronous'] = ('is_synchronous' in request['queryStringParameters'])
    return qparams

def upload_body(body, object_key=None):
    logger.info('Asynchronous processing...')
    if object_key == None:
        object_key = '{}'.format(uuid.uuid4())
    tmp_file = Path('/tmp/{}'.format(uuid.uuid4()))
    open(str(tmp_file), 'wb').write(body)
    hopper_bucket = os.environ['HopperBucket']
    logger.info('Uploading {} to bucket {} using key {}'.format(str(tmp_file), hopper_bucket, object_key))
    s3_client.upload_file(str(tmp_file), hopper_bucket, object_key)
    return {
        'statusCode': HTTPStatus.ACCEPTED,
        'headers': {}
    }

def process_body(body):
    logger.info('Synchronous processing...')
    tmp_path = Path('/tmp')
    local_source_filepath = Path('/tmp/{}'.format(uuid.uuid4()))
    open(str(local_source_filepath), 'wb').write(body)
    local_descriptor_filepath = Path('/tmp/{}'.format(uuid.uuid4()))
    local_result_filepath = Path('/tmp/{}'.format(uuid.uuid4()))
    task.do_task(str(tmp_path),
        str(local_source_filepath),
        str(local_descriptor_filepath),
        str(local_result_filepath))
    local_result_bytes = open(str(local_result_filepath), 'rb').read()
    local_result = local_result_bytes.decode()
    body = json.dumps(local_result, indent=4)
    #'Content-Length': len(local_result_bytes)
    return {
        'statusCode': HTTPStatus.OK,
        'headers': { 'Content-Type': 'application/json' },
        'body': body
    }

