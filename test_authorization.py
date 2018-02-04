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
        logger.error("FAIL::test_base64 (decoded value mutated)")
        exit(1)

def test_token_valid():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) + 30
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    logger.debug("authorization_header=[{}]".format(authorization_header))
    if module_under_test.token_valid(authorization_header, secret):
        logger.info("PASS::test_token_valid")
    else:
        logger.error("FAIL::test_token_valid")
        exit(1)

def test_environment_valid():
    secret = os.environ['API_SECRET']
    authorization_header = os.environ['API_AUTHORIZATION']
    logger.debug("authorization_header=[{}]".format(authorization_header))
    if module_under_test.token_valid(authorization_header, secret):
        logger.info("PASS::test_environment_valid")
    else:
        logger.error("FAIL::test_environment_valid")
        exit(1)

def test_token_invalid_missing_expires():
    user = 'user-{}'.format(uuid.uuid4())
    expires = None
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    if not module_under_test.token_valid(authorization_header, secret):
        logger.info("PASS::test_token_invalid_missing_expires")
    else:
        logger.error("FAIL::test_token_invalid_missing_expires")
        exit(1)

def test_token_invalid_missing_user():
    user = None
    expires = int(time.time()) + 30
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    if not module_under_test.token_valid(authorization_header, secret):
        logger.info("PASS::test_token_invalid_missing_user")
    else:
        logger.error("FAIL::test_token_invalid_missing_user")
        exit(1)

def test_token_invalid_signature():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) + 30
    secret = '{}'.format(uuid.uuid4())
    different_secret = uuid.uuid4()
    authorization_header = generate_token(user, expires, secret)
    if not module_under_test.token_valid(authorization_header, different_secret):
        logger.info("PASS::test_token_invalid_signature")
    else:
        logger.error("FAIL::test_token_invalid_signature")
        exit(1)

def test_token_current():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) + 30
    current_time = time.time()
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    if module_under_test.is_current(authorization_header, current_time):
        logger.info("PASS::test_token_current")
    else:
        logger.error("FAIL::test_token_current")
        exit(1)

def test_token_expired():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) - 30
    current_time = time.time()
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    if not module_under_test.is_current(authorization_header, current_time):
        logger.info("PASS::test_token_expired")
    else:
        logger.error("FAIL::test_token_expired")
        exit(1)

def test_token_user():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) - 30
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    if module_under_test.get_user(authorization_header) == user:
        logger.info("PASS::test_token_user")
    else:
        logger.error("FAIL::test_token_user")
        exit(1)

def test_token_not_user():
    user = 'user-{}'.format(uuid.uuid4())
    different_user = 'different-user-{}'.format(uuid.uuid4())
    expires = int(time.time()) - 30
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(different_user, expires, secret)
    if module_under_test.get_user(authorization_header) != user:
        logger.info("PASS::test_token_not_user")
    else:
        logger.error("FAIL::test_token_not_user")
        exit(1)

def test_token_expires():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) - 30
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, expires, secret)
    if module_under_test.get_expires(authorization_header) == expires:
        logger.info("PASS::test_token_expires")
    else:
        logger.error("FAIL::test_token_expires")
        exit(1)

def test_token_not_expires():
    user = 'user-{}'.format(uuid.uuid4())
    expires = int(time.time()) + 30
    different_expires = int(time.time()) + 20
    secret = '{}'.format(uuid.uuid4())
    authorization_header = generate_token(user, different_expires, secret)
    if module_under_test.get_expires(authorization_header) != expires:
        logger.info("PASS::test_token_not_expires")
    else:
        logger.error("FAIL::test_token_not_expires")
        exit(1)

def generate_token(user, expires, secret):
    token_descriptor = {}
    if user != None:
        token_descriptor['user'] = user
    if expires != None:
        token_descriptor['expires'] = expires
    authorization_user = module_under_test.string_to_base64_encoded_string(json.dumps(token_descriptor))
    #logger.debug('authorization_user=[{}]'.format(authorization_user))
    string_to_sign = '{}{}'.format(secret, 
        authorization_user)
    logger.debug('string_to_sign=[{}]'.format(string_to_sign))
    bytes_to_sign = string_to_sign.encode()
    hash = sha256()
    hash.update(bytes_to_sign)
    authorization_signature = hash.hexdigest()
    logger.debug('authorization_signature=[{}]'.format(authorization_signature))
    return 'Bearer {}.{}'.format(authorization_user, authorization_signature)

def run_tests():
    test_base64()
    test_token_valid()
    test_environment_valid()
    test_token_invalid_missing_expires()
    test_token_invalid_missing_user()
    test_token_invalid_signature()
    test_token_current()
    test_token_expired()
    test_token_user()
    test_token_not_user()
    test_token_expires()
    test_token_not_expires()

run_tests()
