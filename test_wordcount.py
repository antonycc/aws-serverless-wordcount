#!/usr/bin/env python3
# Purpose: Handle the AWS native elements then hand off a word count

import os
import shutil
import uuid
import logging
import task_wordcount as task
from pathlib import Path
import yaml

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def process_all_records(records):
    logger.info('Processing all records...')
    config = yaml.load(Path("./serverless_wordcount.yaml").read_text())
    environment_variables = config['Resources']['CopyFunction']['Properties']['Environment']['Variables']
    tmp_path = Path('./tmp')
    hopper_bucket = Path('{}/hopper'.format(tmp_path))
    result_postfix = environment_variables['ResultPostfix']
    result_bucket = Path('{}/{}'.format(tmp_path, environment_variables['ResultBucket']))
    archive_bucket = Path('{}/{}'.format(tmp_path, environment_variables['ArchiveBucket']))
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

    local_result_filepath = Path('{}/local/{}'.format(tmp_path, uuid.uuid4()))
    task.do_task(tmp_path, str(local_source_filepath), str(local_result_filepath))

    result_filepath = Path('{}/{}{}'.format(result_bucket, object_key, result_postfix))
    shutil.copy(str(local_result_filepath), str(result_filepath))
    logger.info('Created {}'.format(str(result_filepath)))

    archive_filepath = Path('{}/{}'.format(archive_bucket, object_key))
    shutil.copy(str(local_source_filepath), str(archive_filepath))
    logger.info('Created {}'.format(archive_filepath))

process_all_records(['fragments-to-process-100.tar.gz'])