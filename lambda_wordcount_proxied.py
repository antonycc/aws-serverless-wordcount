#!/usr/bin/env python3
# Purpose: Read a body and submit for a wordcount

import base64
import json
import logging
import os
from http import HTTPStatus
from pathlib import Path

import time

import task_wordcount as task
import utils_authorization as auth
import utils_s3 as utils_s3
import utils_transform as transform

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(request, context):
    log_request_response('REQUEST:', request)
    if 'resource' in request:
        api_secret = os.environ['ApiSecret']
        authorization_header = request['headers']['Authorization']
        current_time = int(time.time())
        response = web_handler(request, authorization_header, api_secret, current_time)
        log_request_response('RESPONSE:', request)
        return response
    else:
        logger.info('No resource identified in request to process.')


def log_request_response(event, payload):
    logger.debug(event)
    logger.debug(json.dumps(transform.filter_dict(payload, ['body'], 20)))


def web_handler(request, authorization_header, api_secret, current_time):
    response = auth.auth_header_valid(authorization_header, api_secret, current_time)
    if response['statusCode'] != HTTPStatus.OK:
        return response
    elif request['httpMethod'] == 'GET':
        if request['resource'] == '/health':
            return get_health_handler(request, response)
        else:
            return get_wordcount_handler(request, response)
    elif request['httpMethod'] == 'POST':
        return post_wordcount_handler(request, response)
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


def get_health_handler(request, response):
    hopper_bucket = os.environ['HopperBucket']
    result_bucket = os.environ['ResultBucket']
    postfix = os.environ['ResultPostfix']
    health = {
        's3': utils_s3.get_s3_health([hopper_bucket, result_bucket])
    }
    if health['s3']['health_check_passed']:
        response['statusCode'] = HTTPStatus.OK
    else:
        response['statusCode'] = HTTPStatus.SERVICE_UNAVAILABLE
    response['body'] = json.dumps(health)
    return response


def get_wordcount_handler(request, response):
    result_bucket = os.environ['ResultBucket']
    postfix = os.environ['ResultPostfix']
    resource = os.path.basename(request['path'])
    object_key = '{}{}'.format(resource, postfix)
    if utils_s3.object_exists(result_bucket, object_key):
        tmp_path = Path('/tmp')
        result = utils_s3.read_object_to_json(tmp_path, result_bucket, object_key)
        response['statusCode'] = HTTPStatus.OK
        response['body'] = json.dumps(result)
        return response
    else:
        response['statusCode'] = HTTPStatus.NOT_FOUND
        return response


def post_wordcount_handler(request, response):
    body = base64.b64decode(request['body'])
    qparams = get_query_string_parameters(request)
    hopper_bucket = os.environ['HopperBucket']
    tmp_path = Path('/tmp')
    if qparams['is_synchronous']:
        local_source_filepath = utils_s3.body_to_local(tmp_path, body)
        result = task.do_task(str(tmp_path), str(local_source_filepath), None, None)
        response['statusCode'] = HTTPStatus.OK
        response['body'] = json.dumps(result)
        return response
    else:
        resource = utils_s3.body_to_s3(tmp_path, body, hopper_bucket, qparams['filename'])
        response['statusCode'] = HTTPStatus.ACCEPTED
        response['headers']['Location'] = '/wordcount/{}'.format(resource)
        return response
