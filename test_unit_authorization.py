#!/usr/bin/env python3
# Purpose: Handle the AWS native elements then hand off a word count

import os
import shutil
import uuid
import time
import json
import base64
import logging
import utils_authorization as module_under_test
import utils_transform as transform
from hashlib import sha256

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def test_auth_header_valid():
    user = 'user-{}'.format(uuid.uuid4())
    current_time = time.time()
    expires = int(time.time()) + 30
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    logger.debug("authorization_header=[{}]".format(authorization_header))
    assert module_under_test.auth_header_valid(authorization_header, secret, current_time)

def test_token_valid():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) + 30
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    logger.debug("authorization_header=[{}]".format(authorization_header))
    assert  module_under_test.token_valid(authorization_header, secret)

def test_token_invalid_missing_expires():
    user = 'user-{}'.format(uuid.uuid4())
    expires = None
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    assert not module_under_test.token_valid(authorization_header, secret)

def test_token_invalid_missing_user():
    user = None
    expires = int(time.time()) + 30
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    assert not module_under_test.token_valid(authorization_header, secret)

def test_token_invalid_signature():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) + 30
    secret = '{}'.format(uuid.uuid4())
    different_secret = uuid.uuid4()
    authorization_header = generate_token(user, expires, secret)
    assert not module_under_test.token_valid(authorization_header, different_secret)

def test_token_current():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) + 30
    current_time = time.time()
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    assert module_under_test.is_current(authorization_header, current_time)

def test_token_expired():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) - 30
    current_time = time.time()
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    assert not module_under_test.is_current(authorization_header, current_time)

def test_token_user():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) - 30
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    assert module_under_test.get_user(authorization_header) == user

def test_token_not_user():
    user = 'user-{}'.format(uuid.uuid4())
    different_user = 'different-user-{}'.format(uuid.uuid4())
    expires = int(time.time()) - 30
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(different_user, expires, secret)
    assert module_under_test.get_user(authorization_header) != user

def test_token_expires():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) - 30
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    assert module_under_test.get_expires(authorization_header) == expires

def test_token_not_expires():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) + 30
    different_expires = int(time.time()) + 20
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, different_expires, secret)
    assert module_under_test.get_expires(authorization_header) != expires

def generate_token(user, expires, secret):
    token_descriptor = {}
    if user != None:
        token_descriptor['user'] = user
    if expires != None:
        token_descriptor['expires'] = expires
    authorization_user = transform.string_to_base64_encoded_string(json.dumps(token_descriptor))
    logger.debug('authorization_user=[{}]'.format(authorization_user))
    string_to_sign = '{}{}'.format(secret, 
        authorization_user)
    logger.debug('string_to_sign=[{}]'.format(string_to_sign))
    bytes_to_sign = string_to_sign.encode()
    hash = sha256()
    hash.update(bytes_to_sign)
    authorization_signature = hash.hexdigest()
    logger.debug('authorization_signature=[{}]'.format(authorization_signature))
    return 'Bearer {}.{}'.format(authorization_user, authorization_signature)
