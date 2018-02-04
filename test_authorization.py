#!/usr/bin/env python3
# Purpose: Handle the AWS native elements then hand off a word count

import os
import shutil
import uuid
import logging
import utils_authorization as module_under_test
from pathlib import Path
from hashlib import sha256

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def test_token_valid():
    user = uuid.uuid4()
    expires = time.time() + 30
    secret = uuid.uuid4()
    authorization_header = generate_token(user, expires, secret)
    if module_under_test.token_valid(authorization_header, secret):
        logger.info("PASS::test_token_valid")
    else:
        logger.info("FAIL::test_token_valid")

def test_token_invalid_missing_expires():
    user = uuid.uuid4()
    expires = None
    secret = uuid.uuid4()
    authorization_header = generate_token(user, expires, secret)
    if not module_under_test.token_valid(authorization_header, secret):
        logger.info("PASS::test_token_invalid_missing_expires")
    else:
        logger.info("FAIL::test_token_invalid_missing_expires")

def test_token_invalid_missing_user():
    user = None
    expires = time.time() + 30
    secret = uuid.uuid4()
    authorization_header = generate_token(user, expires, secret)
    if not module_under_test.token_valid(authorization_header, secret):
        logger.info("PASS::test_token_invalid_missing_user")
    else:
        logger.info("FAIL::test_token_invalid_missing_user")

def test_token_invalid_signature():
    user = uuid.uuid4()
    expires = time.time() + 30
    secret = uuid.uuid4()
    different_secret = uuid.uuid4()
    authorization_header = generate_token(user, expires, secret)
    if not module_under_test.token_valid(authorization_header, different_secret):
        logger.info("PASS::test_token_valid")
    else:
        logger.info("FAIL::test_token_valid")

def test_token_current():
    user = uuid.uuid4()
    expires = time.time() + 30
    current_time = time.time()
    secret = uuid.uuid4()
    authorization_header = generate_token(user, expires, secret)
    if module_under_test.is_current(authorization_header, current_time):
        logger.info("PASS::test_token_current")
    else:
        logger.info("FAIL::test_token_current")

def test_token_expired():
    user = uuid.uuid4()
    expires = time.time() - 30
    current_time = time.time()
    secret = uuid.uuid4()
    authorization_header = generate_token(user, expires, secret)
    if not module_under_test.is_current(authorization_header, current_time):
        logger.info("PASS::test_token_expired")
    else:
        logger.info("FAIL::test_token_expired")

def test_token_user():
    user = uuid.uuid4()
    expires = time.time() - 30
    current_time = time.time()
    secret = uuid.uuid4()
    authorization_header = generate_token(user, expires, secret)
    if module_under_test.get_user(authorization_header) == user:
        logger.info("PASS::test_token_expired")
    else:
        logger.info("FAIL::test_token_expired")

def test_token_not_user():
    user = uuid.uuid4()
    different_user = uuid.uuid4()
    expires = time.time() - 30
    current_time = time.time()
    secret = uuid.uuid4()
    authorization_header = generate_token(different_user, expires, secret)
    if module_under_test.get_user(authorization_header) != user:
        logger.info("PASS::test_token_expired")
    else:
        logger.info("FAIL::test_token_expired")

def run_tests():
    test_token_valid()
    test_token_invalid_missing_expires()
    test_token_invalid_missing_user()
    test_token_invalid_signature()
    test_token_current()
    test_token_expired()
    test_token_user()
