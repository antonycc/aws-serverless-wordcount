#!/usr/bin/env python3
# Purpose: Authorization utilitites primerily to inspect the Authorization header

import base64
import json
import logging
import re
from hashlib import sha256
from http import HTTPStatus

logger = logging.getLogger()

authorization_header_prefix = re.compile("Bearer ")
authorization_header_split = re.compile("\.")


def auth_header_valid(authorization_header, api_secret, current_time):
    if not token_valid(authorization_header, api_secret):
        return {
            'statusCode': HTTPStatus.UNAUTHORIZED,
            'headers': {}
        }
    elif not is_current(authorization_header, current_time):
        return {
            'statusCode': HTTPStatus.FORBIDDEN,
            'headers': {}
        }
    else:
        user = get_user(authorization_header)
        expires = get_expires(authorization_header)
        logger.info('Accepted bearer token for: {} (expires:{})'.format(user, expires))
        return {
            'statusCode': HTTPStatus.OK,
            'headers': {}
        }


def token_valid(authorization_header, api_secret):
    logger.info("Checking authorization_header=[{}]".format(authorization_header))
    logger.debug("with secret=[{}]".format(api_secret))
    authorization_header_components = extract_header_components(authorization_header)
    if len(authorization_header_components) != 2:
        logger.debug("Expected 2 components found {}".format(len(authorization_header_components)))
        return False
    else:
        authorization_user = authorization_header_components[0]
        authorization_signature = authorization_header_components[1]
        string_to_sign = '{}{}'.format(api_secret, authorization_user)
        generated_signature = generate_signature(string_to_sign)
        logger.info("generated_signature=[{}]".format(generated_signature))
        if authorization_signature == generated_signature:
            token_descriptor = extract_token_descriptor(authorization_header_components)
            return ('expires' in token_descriptor) and ('user' in token_descriptor)


def is_current(authorization_header, current_time):
    authorization_header_components = extract_header_components(authorization_header)
    if len(authorization_header_components) != 2:
        logger.debug("Expected 2 components found {}".format(len(authorization_header_components)))
        return False
    else:
        token_descriptor = extract_token_descriptor(authorization_header_components)
        expires = int(token_descriptor['expires'])
        logger.debug("Token expires at {} and current time {}".format(expires, current_time))
        return current_time < expires


def get_user(authorization_header):
    authorization_header_components = extract_header_components(authorization_header)
    if len(authorization_header_components) != 2:
        logger.debug("Expected 2 components found {}".format(len(authorization_header_components)))
        return None
    else:
        token_descriptor = extract_token_descriptor(authorization_header_components)
        user = token_descriptor['user']
        logger.debug("Token identified by user {}".format(user))
        return user


def get_expires(authorization_header):
    authorization_header_components = extract_header_components(authorization_header)
    if len(authorization_header_components) != 2:
        logger.debug("Expected 2 components found {}".format(len(authorization_header_components)))
        return None
    else:
        token_descriptor = extract_token_descriptor(authorization_header_components)
        expires = token_descriptor['expires']
        logger.debug("Token expires {}".format(expires))
        return expires


def extract_header_components(authorization_header):
    authorization_header_value = authorization_header_prefix.sub("", authorization_header)
    return authorization_header_split.split(authorization_header_value)


def extract_token_descriptor(authorization_header_components):
    authorization_user = authorization_header_components[0]
    token_descriptor_string = base64.b64decode(authorization_user)
    return json.loads(token_descriptor_string)


def generate_signature(string_to_sign):
    logger.debug('string_to_sign=[{}]'.format(string_to_sign))
    bytes_to_sign = string_to_sign.encode()
    hash = sha256()
    hash.update(bytes_to_sign)
    signature = hash.hexdigest()
    logger.debug('signature=[{}]'.format(signature))
    return signature
