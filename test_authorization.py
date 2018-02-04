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
from pathlib import Path
from hashlib import sha256

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def test_base64():
    key = 'key-{}'.format(uuid.uuid4())
    expected_value = 'value-{}'.format(uuid.uuid4())
    obj = { key: expected_value}
    expected_string = json.dumps(obj)
    encoded = module_under_test.string_to_base64_encoded_string(expected_string)
    decoded = module_under_test.base64_encoded_string_to_string(encoded)
    #logger.debug("encoded=[{}]".format(encoded))
    if expected_string == encoded:
        logger.info("FAIL::test_base64 (encoded string is unchanged)")
    if expected_string != decoded:
        logger.info("FAIL::test_base64 (decoded string does not match original)")
    decoded_obj = json.loads(decoded)
    decoded_value = decoded_obj[key]
    if expected_value == decoded_value:
        logger.info("PASS::test_base64")
    else:
        logger.info("FAIL::test_base64 (decoded value mutated)")

def test_token_valid():
    user = 'user-{}'.format(uuid.uuid4())
    expires = time.time() + 30
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    logger.debug("authorization_header=[{}]".format(authorization_header))
    if module_under_test.token_valid(authorization_header, secret):
        logger.info("PASS::test_token_valid")
    else:
        logger.info("FAIL::test_token_valid")

def test_token_invalid_missing_expires():
    user = 'user-{}'.format(uuid.uuid4())
    expires = None
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    if not module_under_test.token_valid(authorization_header, secret):
        logger.info("PASS::test_token_invalid_missing_expires")
    else:
        logger.info("FAIL::test_token_invalid_missing_expires")

def test_token_invalid_missing_user():
    user = None
    expires = time.time() + 30
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    if not module_under_test.token_valid(authorization_header, secret):
        logger.info("PASS::test_token_invalid_missing_user")
    else:
        logger.info("FAIL::test_token_invalid_missing_user")

def test_token_invalid_signature():
    user = 'user-{}'.format(uuid.uuid4())
    expires = time.time() + 30
    secret = '{}'.format(uuid.uuid4())
    different_secret = uuid.uuid4()
    authorization_header = generate_token(user, expires, secret)
    if not module_under_test.token_valid(authorization_header, different_secret):
        logger.info("PASS::test_token_invalid_signature")
    else:
        logger.info("FAIL::test_token_invalid_signature")

def test_token_current():
    user = 'user-{}'.format(uuid.uuid4())
    expires = time.time() + 30
    current_time = time.time()
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    if module_under_test.is_current(authorization_header, current_time):
        logger.info("PASS::test_token_current")
    else:
        logger.info("FAIL::test_token_current")

def test_token_expired():
    user = 'user-{}'.format(uuid.uuid4())
    expires = time.time() - 30
    current_time = time.time()
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    if not module_under_test.is_current(authorization_header, current_time):
        logger.info("PASS::test_token_expired")
    else:
        logger.info("FAIL::test_token_expired")

def test_token_user():
    user = 'user-{}'.format(uuid.uuid4())
    expires = time.time() - 30
    current_time = time.time()
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    if module_under_test.get_user(authorization_header) == user:
        logger.info("PASS::test_token_expired")
    else:
        logger.info("FAIL::test_token_expired")

def test_token_not_user():
    user = 'user-{}'.format(uuid.uuid4())
    different_user = 'different-user-{}'.format(uuid.uuid4())
    expires = time.time() - 30
    current_time = time.time()
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(different_user, expires, secret)
    if module_under_test.get_user(authorization_header) != user:
        logger.info("PASS::test_token_expired")
    else:
        logger.info("FAIL::test_token_expired")

def generate_token(user, expires, secret):
    token_descriptor = {}
    if user != None:
        token_descriptor['user'] = user
    if expires != None:
        token_descriptor['expires'] = expires
    authorization_user = module_under_test.string_to_base64_encoded_string(json.dumps(token_descriptor))
    #logger.debug('authorization_user=[{}]'.format(authorization_user))
    string_to_sign = '{}{}'.format(authorization_user, secret)
    bytes_to_sign = string_to_sign.encode()
    hash = sha256()
    hash.update(bytes_to_sign)
    digest = hash.digest()
    authorization_signature_bytes = base64.b64encode(digest)
    authorization_signature = authorization_signature_bytes.decode()
    return '{}.{}'.format(authorization_user, authorization_signature)

def run_tests():
    test_base64()
    test_token_valid()
    test_token_invalid_missing_expires()
    test_token_invalid_missing_user()
    test_token_invalid_signature()
    test_token_current()
    test_token_expired()
    test_token_user()
    test_token_not_user()

run_tests()