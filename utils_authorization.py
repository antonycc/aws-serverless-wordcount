#!/usr/bin/env python3
# Purpose: Authorization utilitites primerily to inspect the Authorization header

import logging
import json
import time
import base64
from hashlib import sha256
import re

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

authorization_header_prefix = re.compile("Bearer ")
authorization_header_split = re.compile(".")

def token_valid(authorization_header, api_secret):
    authorization_header_components = extract_header_components(authorization_header)
    if len(authorization_header_components) != 2:
        return false
    else:
        authorization_user = authorization_header_components[0]
        authorization_signature = authorization_header_components[1]
        generated_signature = generate_signature(authorization_user, api_secret)
        return authorization_signature == generated_signature and
            'expires' in token_descriptor and
            'user' in token_descriptor

def is_current(authorization_header, current_time):
    authorization_header_components = extract_header_components(authorization_header)
    if len(authorization_header_components) != 2:
        return false
    else:
        token_descriptor = extract_token_descriptor(authorization_header_components)
        expires = token_descriptor['expires']
        logger.info("API token expires {}, current time {}".format(expires, current_time))
        return current_time < expires

def get_user(authorization_header):
    authorization_header_components = extract_header_components(authorization_header)
    if len(authorization_header_components) != 2:
        return false
    else:
        token_descriptor = extract_token_descriptor(authorization_header_components)
        user = token_descriptor['user']
        logger.info("API request identified by user {}".format(user))
        return user

def extract_header_components(authorization_header):
    authorization_header_value = authorization_header_prefix.sub("", s)
    return authorization_header_split.split("", authorization_header_value)

def extract_token_descriptor(authorization_header_components):
    authorization_user = authorization_header_components[0]
    token_descriptor_string = base64.b64decode(authorization_user)
    return json.parse(token_descriptor_string)

def generate_signature(authorization_user, api_secret):
    hash = hashlib.sha256()
    authorization_user_bytes = str.encode(authorization_user)
    hash.update(authorization_user_bytes)
    return hash.digest()
