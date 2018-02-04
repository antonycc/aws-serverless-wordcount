#!/usr/bin/env python3
# Purpose: Authorization utilitites primerily to inspect the Authorization header

import logging
import json
import zlib
import time
import base64
from hashlib import sha256
import re

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

authorization_header_prefix = re.compile("Bearer ")
authorization_header_split = re.compile("\.")

def token_valid(authorization_header, api_secret):
    authorization_header_components = extract_header_components(authorization_header)
    if len(authorization_header_components) != 2:
        logger.debug("Expected 2 components found {}".format(len(authorization_header_components)))
        return False
    else:
        authorization_user = authorization_header_components[0]
        authorization_signature = authorization_header_components[1]
        string_to_sign = '{}{}'.format(authorization_user, api_secret)
        generated_signature = generate_signature(string_to_sign)
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
        expires = token_descriptor['expires']
        logger.info("Token expires at {} and current time {}".format(expires, current_time))
        return current_time < expires

def get_user(authorization_header):
    authorization_header_components = extract_header_components(authorization_header)
    if len(authorization_header_components) != 2:
        logger.debug("Expected 2 components found {}".format(len(authorization_header_components)))
        return None
    else:
        token_descriptor = extract_token_descriptor(authorization_header_components)
        user = token_descriptor['user']
        logger.info("Token identified by user {}".format(user))
        return user

def extract_header_components(authorization_header):
    authorization_header_value = authorization_header_prefix.sub("", authorization_header)
    return authorization_header_split.split(authorization_header_value)

def extract_token_descriptor(authorization_header_components):
    authorization_user = authorization_header_components[0]
    token_descriptor_string = base64.b64decode(authorization_user)
    return json.loads(token_descriptor_string)

def generate_signature(string_to_sign):
    bytes_to_sign = string_to_sign.encode()
    hash = sha256()
    hash.update(bytes_to_sign)
    digest = hash.digest()
    signature_bytes = base64.b64encode(digest)
    signature = signature_bytes.decode()
    logger.debug("signature=[{}]".format(signature))
    return signature

def string_to_base64_encoded_string(s1):
    #logger.debug('encode: s1=[{}]'.format(s1))
    s2 = s1.encode()
    #logger.debug('encode: s2=[{}]'.format(s2))
    s3 = base64.b64encode(s2)
    #logger.debug('encode: s3=[{}]'.format(s3))
    s4 = s3.decode()
    #logger.debug('encode: s4=[{}]'.format(s4))
    return s4

def base64_encoded_string_to_string(s1):
    #logger.debug('decode: s1=[{}]'.format(s1))
    s2 = s1.encode()
    #logger.debug('decode: s2=[{}]'.format(s2))
    s3 = base64.b64decode(s2)
    #logger.debug('decode: s3=[{}]'.format(s3))
    s4 = s3.decode()
    #logger.debug('decode: s4=[{}]'.format(s4))
    return s4


