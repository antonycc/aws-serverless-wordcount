#!/usr/bin/env python3
# Purpose: Batch of all tests

import logging
import test_unit_transform
import test_unit_authorization
import test_unit_s3

# Modules not exercised but imported so they are parsed
import lambda_wordcount_proxied
import utils_s3 as utils_s3

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def run_tests():
    test_unit_transform.run_tests()
    test_unit_authorization.run_tests()
    test_unit_s3.run_tests()
    
run_tests()
