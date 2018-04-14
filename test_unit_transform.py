#!/usr/bin/env python3
# Purpose: Object and string transformation tests

import json
import logging
import uuid

import utils_transform as module_under_test

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def test_base64():
    key = 'key-{}'.format(uuid.uuid4())
    expected_value = 'value-{}'.format(uuid.uuid4())
    obj = {key: expected_value}
    expected_string = json.dumps(obj)
    encoded = module_under_test.string_to_base64_encoded_string(expected_string)
    decoded = module_under_test.base64_encoded_string_to_string(encoded)
    # logger.debug("encoded=[{}]".format(encoded))
    if expected_string == encoded:
        logger.info("FAIL::test_base64 (encoded string is unchanged)")
    if expected_string != decoded:
        logger.info("FAIL::test_base64 (decoded string does not match original)")
    decoded_obj = json.loads(decoded)
    decoded_value = decoded_obj[key]
    assert expected_value == decoded_value


def test_filter_dict():
    keep = 'keep'
    filter = 'filter'
    d1 = {keep: 'this', 'and': '', filter: 'that-out'}
    ks = [filter]
    n = 4
    d2 = module_under_test.filter_dict(d1, ks, n)
    assert (d2[keep] == 'this') and (d2[filter] == 'that')
