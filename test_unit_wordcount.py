#!/usr/bin/env python3
# 

import logging
import task_wordcount as module_under_test

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def test_clean_text():
    s1 = 'a\u2122b\u0160c'
    s2 = 'ab c'
    assert module_under_test.clean_text(s1) == s2
