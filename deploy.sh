#!/bin/bash

# Prepare source files for distribution
mkdir -p "./target/dist"
cp "./lambda_wordcount.py" "./target/dist/."
cp "./task_wordcount.py" "./target/dist/."

# Package AWS Lambda with Serverless template:
aws cloudformation package \
   --template-file "serverless_wordcount.yaml" \
   --output-template-file "serverless_wordcount_output.yaml" \
   --s3-bucket "serverless-wordcount-deploy"

# Deploy AWS Lambda with Serverless template:
aws cloudformation deploy \
   --template-file "serverless_wordcount_output.yaml" \
   --stack-name "serverless-wordcount-stack" \
   --capabilities CAPABILITY_IAM

# Clean up
rm -rf "./target/dist"