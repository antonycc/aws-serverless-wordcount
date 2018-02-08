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
    logger.debug(json.dumps(auth.filter_dict(request, ['body'], 20)))
    api_secret = os.environ['ApiSecret']
    authorization_header = request['headers']['Authorization']
    current_time = int(time.time())
    response = web_handler(request, authorization_header, api_secret, current_time)
    logger.debug('RESPONSE:')
    logger.debug(json.dumps(auth.filter_dict(response, ['body'], 20)))
    return response

def web_handler(request, authorization_header, api_secret, current_time):
    response = auth.auth_header_valid(authorization_header, api_secret, current_time)
    if response['statusCode'] != HTTPStatus.OK:
        return response
    elif request['httpMethod'] == 'GET':
        return get_handler(request, response)
    elif request['httpMethod'] == 'POST':
        return post_handler(request, response)
    else:
        response['statusCode'] = HTTPStatus.METHOD_NOT_ALLOWED
        return response

def get_handler(request, response):
    # TODO: GET the resource from the URL path
    object_key = 'dummy-pass'
    # TODO: If the resource exists in the result bucket
    exists = False
    if exists or (object_key == 'dummy-pass'):
        # TODO: READ the resource
        result = {'dummy-pass': '{}'.format(True)}
        response['statusCode'] = HTTPStatus.OK
        #result_bytes = result.encode()
        response['body'] = json.dumps(result)
        #response['headers']['Content-Length'] = '{}'.format(len(result_bytes))
        return response
    else:
        response['statusCode'] = HTTPStatus.NOT_FOUND
        return response

def post_handler(request, response):
    body = base64.b64decode(request['body'])
    qparams = get_query_string_parameters(request)
    if qparams['is_synchronous']:
        result = process_body(body)
        response['statusCode'] = HTTPStatus.OK
        #'Content-Length': len(local_result_bytes)
        response['body'] = json.dumps(result)
        return response
    else:
        resource = upload_body(body, qparams['filename'])
        response['statusCode'] = HTTPStatus.ACCEPTED
        response['headers']['Location'] = '/wordcount/{}'.format(resource)
        return response

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

def process_body(body):
    logger.info('Synchronous processing...')
    tmp_path = Path('/tmp')
    local_source_filepath = Path('/tmp/{}'.format(uuid.uuid4()))
    open(str(local_source_filepath), 'wb').write(body)
    local_descriptor_filepath = Path('/tmp/{}'.format(uuid.uuid4()))
    local_result_filepath = Path('/tmp/{}'.format(uuid.uuid4()))
    result = task.do_task(str(tmp_path), str(local_source_filepath), str(local_descriptor_filepath), None)
    return result

def upload_body(body, object_key=None):
    logger.info('Asynchronous processing...')
    if object_key == None:
        object_key = '{}'.format(uuid.uuid4())
    tmp_file = Path('/tmp/{}'.format(uuid.uuid4()))
    open(str(tmp_file), 'wb').write(body)
    hopper_bucket = os.environ['HopperBucket']
    logger.info('Uploading {} to bucket {} using key {}'.format(str(tmp_file), hopper_bucket, object_key))
    s3_client.upload_file(str(tmp_file), hopper_bucket, object_key)
    return object_key