#!/usr/bin/env python3
# Purpose: Read a body and submit for a wordcount

import os
import logging
import json
import time
import uuid
import base64
from http import HTTPStatus
from pathlib import Path
import utils_authorization as auth
import utils_transform as transform
import utils_s3 as utils_s3
import task_wordcount as task

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(request, context):
    log_request_response('REQUEST:', request)
    api_secret = os.environ['ApiSecret']
    authorization_header = request['headers']['Authorization']
    current_time = int(time.time())
    response = web_handler(request, authorization_header, api_secret, current_time)
    log_request_response('RESPONSE:', request)
    return response

def log_request_response(event, payload):
    logger.debug(event)
    logger.debug(json.dumps(transform.filter_dict(payload, ['body'], 20)))

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

def get_handler(request, response):
    hopper_bucket = os.environ['HopperBucket']
    result_bucket = os.environ['ResultBucket']
    postfix = os.environ['ResultPostfix']
    resource = os.path.basename(request['path'])
    object_key = '{}{}'.format(resource, postfix)
    if resource == 'health':
        health = {
            's3': utils_s3.get_s3_health([hopper_bucket, result_bucket])
        }
        if health['s3']['health_check_passed']:
            response['statusCode'] = HTTPStatus.OK
        else:
            response['statusCode'] = HTTPStatus.SERVICE_UNAVAILABLE
        response['body'] = json.dumps(health)
        return response
    elif utils_s3.object_exists(result_bucket, object_key):
        result = utils_s3.read_json_object(result_bucket, object_key)
        response['statusCode'] = HTTPStatus.OK
        response['body'] = json.dumps(result)
        return response
    else:
        response['statusCode'] = HTTPStatus.NOT_FOUND
        return response

def post_handler(request, response):
    body = base64.b64decode(request['body'])
    qparams = get_query_string_parameters(request)
    hopper_bucket = os.environ['HopperBucket']
    if qparams['is_synchronous']:
        local_source_filepath = utils_s3.body_to_local(body)
        result = task.do_task(str(tmp_path), str(local_source_filepath), None, None)
        response['statusCode'] = HTTPStatus.OK
        response['body'] = json.dumps(result)
        return response
    else:
        resource = utils_s3.body_to_s3(body, hopper_bucket, qparams['filename'])
        response['statusCode'] = HTTPStatus.ACCEPTED
        response['headers']['Location'] = '/wordcount/{}'.format(resource)
        return response



