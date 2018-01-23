#!/bin/bash

aws cloudformation validate-template \
   --template-body "file://serverless.yaml"

aws cloudformation package
   --template-file "serverless.yaml" \
   --output-template-file "serverless_output.yaml" \
   --s3-bucket "serverless-deploy"

aws cloudformation deploy \
   --template-file "serverless_output.yaml" \
   --stack-name "serverless_stack" \
   --capabilities CAPABILITY_IAM

aws cloudformation describe-stacks
