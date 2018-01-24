#!/bin/bash

aws cloudformation package
   --template-file "serverless.yaml" \
   --output-template-file "serverless_output.yaml" \
   --s3-bucket "serverless-deploy"

aws cloudformation deploy \
   --template-file "serverless_output.yaml" \
   --stack-name "serverless-stack" \
   --capabilities CAPABILITY_IAM
