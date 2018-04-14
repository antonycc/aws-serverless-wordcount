#!/usr/bin/env python3
# 

import logging

import lambda_wordcount_triggered as module_under_test

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def test_lambda_handler_no_records():
    event = {}
    context = {}
    module_under_test.lambda_handler(event, context)
    assert True
