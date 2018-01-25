#!/usr/bin/env python3
# Purpose: Count all the words in the fragments

import logging
import boto3
import uuid

# http://docs.python-requests.org/en/master/
# python3 -m pip install requests

# https://github.com/mstamy2/PyPDF2
# python3 -m pip install PyPDF2

# https://pypi.python.org/pypi/timeout-decorator
# python3 -m pip install timeout-decorator

#import re
#import os
#import json
#import shutil
#import logmatic
#import socket
#import logging
#import datetime
#import requests
#from hashlib import sha256
#from pathlib import Path
#import mimetypes
#mimetypes.init()
#import PyPDF2
#import time
#import timeout_decorator
#import config

logger = logging.getLogger()

s3_client = boto3.client('s3')

def wordcount(hopper_bucket, object_key, result_bucket, archive_bucket):
    local_filepath = '/tmp/{}{}'.format(uuid.uuid4(), object_key)
    s3_client.download_file(hopper_bucket, object_key, local_filepath)
    s3_client.upload_file(local_filepath, archive_bucket, object_key)
    logger.info('Created s3://{}/{}'.format(archive_bucket, object_key))

# Read config
#buckets = config.config["buckets"]
#fragments_to_process = buckets["fragments-to-process"]["url"].replace("file://${PWD}/","")
#fragments_archive = buckets["fragments-archive"]["url"].replace("file://${PWD}/","")
#archive_path = buckets["logs-all-archive"]["url"].replace("file://${PWD}/","")

# Constants
#timestamp = datetime.datetime.now().isoformat().replace(":", "-").replace(".", "-")
#logging_filename = "word-count-fragments"
#dest_filepath = os.path.join(fragments_archive, "word-count-" + timestamp + ".json")
#not_alpha = re.compile("[^a-zA-Z]")

# Logging
#logger = logging.getLogger()
#logging_filepath = os.path.join(archive_path, logging_filename + "-" + timestamp + ".log")
#handler = logging.FileHandler(filename=logging_filepath)
#handler.setFormatter(logmatic.JsonFormatter(extra={
#   "hostname": socket.gethostname(),
#   "sourcePath": fragments_to_process,
#   "destPath": dest_filepath
#   }))
#logger.addHandler(handler)
#logger.setLevel(logging.INFO)

#def word_count_fragments(fragments_to_process_path, word_count_filepath):
#   word_count = {}
#   logger.info("Scanning for fragments in: [{}]".format(fragments_to_process_path))
#   for fragment_descriptor_filename in [entry for entry in os.listdir(fragments_to_process_path)]:
#      count_from_fragment_descriptor(fragments_to_process_path, fragment_descriptor_filename, word_count)
#   save_word_count(word_count, word_count_filepath)

#def count_from_fragment_descriptor(fragments_to_process_path, fragment_descriptor_filename, word_count):
#   fragment_descriptor_filepath = os.path.join(fragments_to_process_path, fragment_descriptor_filename)
#   logger.debug("Opening fragment descriptor: [{}]".format(fragment_descriptor_filepath))
#   try:
#      fragment_descriptor_string = Path(fragment_descriptor_filepath).read_text()
#      fragment_descriptor = json.loads(fragment_descriptor_string)
#      fragment = fragment_descriptor["fragment"]
#      count_from_string(fragment, word_count)
#   except Exception as e:
#      logger.error("Error {} reading words from fragment in: [{}]".format(str(e), fragment_descriptor_filename), exc_info=True)

#def count_from_string(string, word_count):
#   words = re.findall(r"\w+|[^\w\s]", string, re.UNICODE)
#
#   for word in words:
#      word = not_alpha.sub('', word)
#      word = word.lower()
#      #word = re.sub(r'([^\s\w]|_)+', '', word)
#      #word = str(filter(str.isalpha, word)).strip()
#      if word:
#         count_word(word, word_count)

#Instead of cleaning up the words here, do it during fragment extraction but get it right here first

#def count_word(word, word_count):
#   #unique_key = "{}".format(word)
#   #word_key = "{}".format(sha256(unique_key.encode("utf-8")).hexdigest())
#   word_key = word
#   if word_key in word_count:
#      #word_count[word_key]["count"] += 1
#      word_count[word_key] += 1
#   else:
#      word_count[word_key] = 1
#      #word_count[word_key] = {
#      #   "word": word,
#      #   "count": 1
#      #}

#def save_word_count(descriptor, target_filename):
#   logger.info("Saving [{}]".format(target_filename))
#   with open(target_filename, 'w') as descriptor_file:
#      json.dump(descriptor, descriptor_file, sort_keys=True, indent=3)

# Main
#word_count_fragments(fragments_to_process, dest_filepath)

