#!/bin/bash

# Package AWS Lambda with Serverless template:
aws cloudformation package \
   --template-file "serverless.yaml" \
   --output-template-file "serverless_output.yaml" \
   --s3-bucket "serverless-deploy-28900"

# Deploy AWS Lambda with Serverless template:
aws cloudformation deploy \
   --template-file "serverless_output.yaml" \
   --stack-name "serverless-stack" \
   --capabilities CAPABILITY_IAM
