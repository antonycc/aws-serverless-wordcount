#!/usr/bin/env python3
# Purpose: Handle the AWS native elements then hand off a word count

import os
import shutil
import uuid
import logging
import task_wordcount as task
from pathlib import Path
from hashlib import sha256

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def process_all_records(records):
    logger.info('Processing all records...')
    tmp_path = Path('./tmp')
    hopper_bucket = Path('{}/hopper'.format(tmp_path))
    result_postfix = '-result.json'
    result_bucket = Path('{}/{}'.format(tmp_path, 'serverless-wordcount-result'))
    archive_bucket = Path('{}/{}'.format(tmp_path, 'serverless-wordcount-archive'))
    hopper_bucket.mkdir(parents=True, exist_ok=True) 
    result_bucket.mkdir(parents=True, exist_ok=True) 
    archive_bucket.mkdir(parents=True, exist_ok=True) 
    Path('{}/local'.format(tmp_path)).mkdir(parents=True, exist_ok=True) 
    for record in records:
        test_filepath = Path('./{}'.format(record))
        shutil.copy(str(test_filepath), str(hopper_bucket))
        process_record(str(tmp_path), str(hopper_bucket), record, str(result_bucket), result_postfix, str(archive_bucket))

def process_record(tmp_path, hopper_bucket, object_key, result_bucket, result_postfix, archive_bucket):
    hopper_object_filepath = Path('{}/{}'.format(hopper_bucket, object_key))
    local_source_filepath = Path('{}/local/{}'.format(tmp_path, uuid.uuid4()))
    shutil.copyfile(str(hopper_object_filepath), str(local_source_filepath))

    filename_prefix = "{}".format(sha256(object_key.encode("utf-8")).hexdigest())
    local_descriptor_filename = "{}-descriptor.json".format(filename_prefi)
    local_descriptor_filepath = Path('{}/local/{}'.format(tmp_path, local_descriptor_filename))
    local_result_filename = "{}-wordcount.json".format(filename_prefi)
    local_result_filepath = Path('{}/local/{}'.format(tmp_path, local_result_filename))
    local_fragment_archive_filename = "{}-fragments.tar.gz".format(filename_prefi)
    local_fragment_archive_filepath = Path('{}/local/{}'.format(tmp_path, local_fragment_archive_filename))
    task.do_task(tmp_path,
        str(local_source_filepath),
        str(local_descriptor_filepath),
        str(local_result_filepath), 
        str(local_fragment_archive_filepath))

    result_filepath = Path('{}/{}{}'.format(result_bucket, object_key, result_postfix))
    shutil.copy(str(local_result_filepath), str(result_filepath))
    logger.info('Created {}'.format(str(result_filepath)))
    descriptor_filepath = Path('{}/{}{}{}'.format(result_bucket, object_key, result_postfix, ".descriptor.json"))
    shutil.copy(str(local_descriptor_filepath), str(descriptor_filepath))
    fragment_archive_filepath = Path('{}/{}{}{}'.format(result_bucket, object_key, result_postfix, ".fragments.tar.gz"))
    shutil.copy(str(local_fragment_archive_filepath), str(fragment_archive_filepath))

    archive_filepath = Path('{}/{}'.format(archive_bucket, object_key))
    shutil.copy(str(local_source_filepath), str(archive_filepath))
    os.remove(str(hopper_object_filepath))
    logger.info('Created {}'.format(archive_filepath))

process_all_records(['ukpga_20100013_en.pdf'])