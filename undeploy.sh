#!/bin/bash
# Remove the stack and any local or remote resources

# Remove resources
aws s3 rm "s3://serverless-wordcount-hopper/" --recursive
aws s3 rm "s3://serverless-wordcount-result/" --recursive
aws s3 rm "s3://serverless-wordcount-archive/" --recursive

# Remove stack
aws cloudformation delete-stack --stack-name "serverless-wordcount-stack"

# Clean up deploy files
rm -f "serverless_wordcount_output.yaml"
rm -rf "./dist"
