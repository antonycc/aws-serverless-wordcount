#!/usr/bin/env python3
# Purpose: Count all the words in the fragments

import os
import logging
import re
import json
#from hashlib import sha256
from pathlib import Path
import tarfile

logger = logging.getLogger()

# Constants
not_alpha = re.compile("[^a-zA-Z]")

def do_task(tmp_path, fragments_to_process_archive_filepath, wordcount_filepath):
   wordcount = {}
   fragments_to_process_path = Path('{}/fragments'.format(tmp_path))
   tar = tarfile.open(fragments_to_process_archive_filepath, "r:gz")
   tar.extractall(str(fragments_to_process_path))
   tar.close()   
   logger.info("Scanning for fragments in: [{}]".format(str(fragments_to_process_path)))
   for fragment_descriptor_filename in [entry for entry in os.listdir(str(fragments_to_process_path))]:
      count_from_fragment_descriptor(fragments_to_process_path, fragment_descriptor_filename, wordcount)
   save_wordcount(wordcount, wordcount_filepath)

def count_from_fragment_descriptor(fragments_to_process_path, fragment_descriptor_filename, wordcount):
   fragment_descriptor_filepath = os.path.join(fragments_to_process_path, fragment_descriptor_filename)
   logger.debug("Opening fragment descriptor: [{}]".format(fragment_descriptor_filepath))
   try:
      fragment_descriptor_string = Path(fragment_descriptor_filepath).read_text()
      fragment_descriptor = json.loads(fragment_descriptor_string)
      fragment = fragment_descriptor["fragment"]
      count_from_string(fragment, wordcount)
   except Exception as e:
      logger.error("Error {} reading words from fragment in: [{}]".format(str(e), fragment_descriptor_filename), exc_info=True)

def count_from_string(string, wordcount):
   words = re.findall(r"\w+|[^\w\s]", string, re.UNICODE)
   for word in words:
      word = not_alpha.sub('', word)
      word = word.lower()
      if word:
         count_word(word, wordcount)

def count_word(word, wordcount):
   word_key = word
   if word_key in wordcount:
      wordcount[word_key] += 1
   else:
      wordcount[word_key] = 1

def save_wordcount(descriptor, target_filename):
   logger.info("Saving [{}]".format(target_filename))
   with open(target_filename, 'w') as descriptor_file:
      json.dump(descriptor, descriptor_file, sort_keys=True, indent=3)


