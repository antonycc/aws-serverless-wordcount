import os
import logging

import task_wordcount as task

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):    
    if 'Records' in event:
        process_all_records(event['Records'])

def process_all_records(records):
    logger.info('Processing all records...')
    result_bucket = os.environ['ResultBucket']
    archive_bucket = os.environ['ArchiveBucket']
    for record in records:
        hopper_bucket = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key'] 
        task.wordcount(hopper_bucket, object_key, result_bucket, archive_bucket)
