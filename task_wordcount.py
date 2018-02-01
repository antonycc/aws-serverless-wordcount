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
import datetime
import PyPDF2
import timeout_decorator

logger = logging.getLogger()

# Constants
not_alpha = re.compile("[^a-zA-Z]")
unwanted_puntuation = re.compile("\u2122")
unwanted_whitespace = re.compile("\n|\u0160|\ufb01|\ufb02")
many_spaces = re.compile(" +")
fragment_separators = re.compile("\.|,|;|:|\-|\+|\*|\?|\|\[|\]|(|)|{|}|\"|\'")

def do_task(tmp_path, pdf_filepath, text_descriptor_filepath, wordcount_filepath):
   fragments = extract_fragments_from_pdf(pdf_filepath)
   text_descriptor = generate_and_save_text_descriptor(pdf_filepath, fragments, text_descriptor_filepath)
   wordcount = generate_and_save_wordcount_from_fragments(fragments, wordcount_filepath)

def generate_and_save_text_descriptor(pdf_filepath, fragments, text_descriptor_filepath):
   text_descriptor = build_text_descriptor(pdf_filepath, fragments)
   logger.info("Saving descriptor for [{}] as [{}]".format(pdf_filepath, text_descriptor_filepath))
   with open(text_descriptor_filepath, 'w') as text_descriptor_file:
      json.dump(text_descriptor, text_descriptor_file, sort_keys=True, indent=3)
   return text_descriptor

def extract_fragments_from_pdf(pdf_filepath):
   pdf_text = read_pdf_text_from_filepath(pdf_filepath)
   s = clean_text(pdf_text)
   return build_fragment_collection(s)

def generate_and_save_wordcount_from_fragments(fragments, wordcount_filepath):
   wordcount = {}
   for fragment in fragments:
      wordcount_from_string(fragment, wordcount)
   save_wordcount(wordcount, wordcount_filepath)
   return wordcount

def build_text_descriptor(text_filepath, fragments):
   timestamp = datetime.datetime.now().isoformat().replace(":", "-").replace(".", "-")
   return {
      "filename": os.path.basename(text_filepath),
      "timestamp": timestamp,
      "type": "pdf_descriptor",
      "fragments": fragments
   }

def read_pdf_text_from_filepath(text_filepath):
   logger.info("Opening PDF [{}]".format(text_filepath))
   with open(text_filepath,"rb") as pdf_file:
      reader = PyPDF2.PdfFileReader(pdf_file)
      text = ""
      for page_number in range(reader.numPages):
         try:
            logger.info("Reading [{}], page: {}".format(text_filepath, page_number))
            text += extract_page_contents(reader, page_number)
         except Exception as e:
            logger.error("Error {} while obtaining page text from: [{}] page {}".format(str(e), text_filepath, page_number), exc_info=True)
      return text

@timeout_decorator.timeout(10, timeout_exception=StopIteration)
def extract_page_contents(reader, page_number):
   return reader.getPage(page_number).extractText()

def clean_text(s):
   logger.info("Cleaning text: Currently {} characters".format(len(s)))
   s = unwanted_puntuation.sub("", s)
   s = unwanted_whitespace.sub(" ", s)
   return many_spaces.sub(" ", s)

def build_fragment_collection(s):
   logger.info("Separating text: Currently {} characters".format(len(s)))
   fragments = fragment_separators.split(s)
   logger.debug("fragments to process[{}]".format(len(fragments)))
   return [ fragment.strip() + "." for fragment in fragments if is_fragment(fragment) ]

def is_fragment(fragment):
   return not (not fragment) and len(fragment.strip()) != 0

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


