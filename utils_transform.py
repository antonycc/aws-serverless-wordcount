#!/usr/bin/env python3
# Purpose: Text and object transformation utilities

import base64
import logging

logger = logging.getLogger()


def string_to_base64_encoded_string(s1):
    # logger.debug('encode: s1=[{}]'.format(s1))
    s2 = s1.encode()
    # logger.debug('encode: s2=[{}]'.format(s2))
    s3 = base64.b64encode(s2)
    # logger.debug('encode: s3=[{}]'.format(s3))
    s4 = s3.decode()
    # logger.debug('encode: s4=[{}]'.format(s4))
    return s4


def base64_encoded_string_to_string(s1):
    # logger.debug('decode: s1=[{}]'.format(s1))
    s2 = s1.encode()
    # logger.debug('decode: s2=[{}]'.format(s2))
    s3 = base64.b64decode(s2)
    # logger.debug('decode: s3=[{}]'.format(s3))
    s4 = s3.decode()
    # logger.debug('decode: s4=[{}]'.format(s4))
    return s4


def filter_dict(d1, ks, n):
    d2 = {}
    for k in d1:
        if (k in ks) and (d1[k] != None):
            d2[k] = d1[k][:n]
        else:
            d2[k] = d1[k]
    return d2
