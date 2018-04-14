#!/usr/bin/env python3
# 

import logging
import shutil
from hashlib import sha256
from pathlib import Path

import task_wordcount as module_under_test

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def test_clean_text():
    s1 = 'a\u2122b\u0160c'
    s2 = 'ab c'
    assert module_under_test.clean_text(s1) == s2


def test_word_count():
    # TODO count the words without requiring a target file
    assert True


def test_word_count_on_physical_file():
    object_key = 'ukpga_20100013_en.pdf'
    result_postfix = '-result.json'

    tmp_path = Path('./tmp')
    shutil.rmtree(str(tmp_path), ignore_errors=True)
    tmp_path.mkdir(parents=True, exist_ok=True)

    local_source_filepath = Path('./{}'.format(object_key))
    filename_prefix = "{}".format(sha256(object_key.encode("utf-8")).hexdigest())
    local_descriptor_filepath = Path('{}/{}-descriptor.json'.format(str(tmp_path), filename_prefix))
    local_result_filepath = Path('{}/{}-wordcount.json'.format(str(tmp_path), filename_prefix))

    module_under_test.do_task(str(tmp_path),
                              str(local_source_filepath),
                              str(local_descriptor_filepath),
                              str(local_result_filepath))

    assert local_descriptor_filepath.exists()
    assert local_result_filepath.exists()

    shutil.rmtree(str(tmp_path), ignore_errors=True)
