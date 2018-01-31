#!/usr/bin/env python3
# Purpose: Count all the words in the fragments

# https://github.com/mstamy2/PyPDF2
# python3 -m pip install PyPDF2

# https://pypi.python.org/pypi/timeout-decorator
# python3 -m pip install timeout-decorator

import os
import logging
import re
import json
from hashlib import sha256
from pathlib import Path
import tarfile
import PyPDF2
import timeout_decorator

logger = logging.getLogger()

# Constants
not_alpha = re.compile("[^a-zA-Z]")

def do_task(tmp_path, pdf_filepath, text_descriptor_filepath, wordcount_filepath, archive_filepath):
   text_descriptor = generate_and_save_text_descriptor(pdf_filepath)
   fragments = extract_fragments_from_pdf(pdf_filepath)
   wordcount = generate_and_save_wordcount_from_fragments(fragments, wordcount_filepath)
   save_fragment_archive(pdf_filepath, fragments, tmp_path, archive_filepath)
   fragments_path = Path('{}/fragments'.format(tmp_path))

def generate_and_save_text_descriptor(pdf_filepath):
   text_descriptor = build_text_descriptor(pdf_filepath)
   logger.info("Saving descriptor for [{}] as [{}]".format(unique_key, target_filename))
   with open(text_descriptor_filepath, 'w') as text_descriptor_file:
      json.dump(text_descriptor, text_descriptor_file, sort_keys=True, indent=3)
   return text_descriptor

def extract_fragments_from_pdf():
   pdf_text = read_pdf_text_from_filepath(pdf_filepath)
   return build_fragment_collection(pdf_text)

def generate_and_save_wordcount_from_fragments(fragments, wordcount_filepath):
   wordcount = {}
   for fragment in fragments:
      wordcount_from_string(fragment, wordcount)
   save_wordcount(wordcount, wordcount_filepath)
   return wordcount

def save_fragment_archive(pdf_filepath, fragments, tmp_path, archive_filepath):
   fragments_path = Path('{}/fragments'.format(tmp_path))
   for fragment in fragments:
      fragment_descriptor = build_fragment_descriptor(text_descriptor, fragment)
      fragment_descriptor_filepath = build_fragment_descriptor_filepath(fragments_path, pdf_filepath, fragment)
      try:
         save_fragment_descriptor(fragment_descriptor, fragment_descriptor_filepath)
      except Exception as e:
         logger.error("Error saving descriptor: {}".format(str(e)), exc_info=True, extra=fragment_descriptor)
   tar = tarfile.open(archive_filepath, 'x:gz')
   tar.add(str(fragments_path))
   tar.close() 

def build_fragment_descriptor_filepath(fragments_path, pdf_filepath, fragment):
   unique_key = "{}{}".format(pdf_filepath, fragment)
   fragment_filename = "{}.json".format(sha256(unique_key.encode("utf-8")).hexdigest())
   return Path.join('{}/{}', fragments_path, fragment_filename)

def build_text_descriptor(text_filepath):
   timestamp = datetime.datetime.now().isoformat().replace(":", "-").replace(".", "-")
   return {
      "filename": text_filepath,
      "timestamp": timestamp,
      "type": "pdf_descriptor"
   }

def build_fragment_descriptor(text_descriptor, fragment):
   timestamp = datetime.datetime.now().isoformat().replace(":", "-").replace(".", "-")
   return {
      "filename": text_descriptor["filename"],
      "timestamp": timestamp,
      "type": "text_descriptor",
      "fragment": fragment
   }

def read_pdf_text_from_filepath(text_filepath):
   logger.info("Opening PDF [{}]".format(text_filepath))
   with open(text_filepath,"rb") as pdf_file:
      reader = PyPDF2.PdfFileReader(pdf_file)
      text = ""
      for page_number in range(reader.numPages):
         try:
            logger.info("Obtaining page text from: [{}] page {}".format(text_filepath, page_number))
            text += extract_page_contents(reader, page_number)
         except Exception as e:
            logger.error("Error {} while obtaining page text from: [{}] page {}".format(str(e), text_filepath, page_number), exc_info=True)
      return text

@timeout_decorator.timeout(10, timeout_exception=StopIteration)
def extract_page_contents(reader, page_number):
   return reader.getPage(page_number).extractText()

def build_fragment_collection(pdf_text):
   fragments = fragment_separators.split(pdf_text)
   logger.debug("fragments [{}]".format(len(fragments)))
   return [ fragment.strip() + "." for fragment in fragments if is_fragment(fragment) ]

def save_fragment_descriptor(descriptor, target_filename):
   logger.info("Saving [{}]".format(target_filename))
   with open(target_filename, 'w') as descriptor_file:
      json.dump(descriptor, descriptor_file, sort_keys=True, indent=3)

def wordcount_from_string(string, wordcount):
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


