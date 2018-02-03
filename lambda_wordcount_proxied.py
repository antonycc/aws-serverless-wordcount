#!/usr/bin/env python3
# Purpose: Read a body and submit for a wordcount

import os
import logging
import json
#import uuid
import base64
import boto3
#import task_wordcount as task
#from pathlib import Path
#from hashlib import sha256

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    request = json.dumps(event, indent=4)
    logger.info("{}".format(request))
    body_bytes = base64.b64decode(event['body'])
    open('/tmp/upload.jpeg', 'wb').write(body_bytes)
    hopper_bucket = os.environ['HopperBucket']
    s3_client.upload_file('/tmp/upload.jpeg', hopper_bucket, 'upload.jpeg')
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": request
    }
