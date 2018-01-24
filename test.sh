#!/bin/bash

# Create a new file and store it in the source bucket:
echo "Serverless test file" > "test.txt"
aws s3 cp "test.txt" "s3://serverless-source-bucket/test.txt"

echo -n "." ; sleep 1 
echo -n "." ; sleep 1
echo -n "." ; sleep 1 
echo -n "." ; sleep 1
echo -n "." ; sleep 1

# Observe that the new file has been copied to the destination bucket and clean up:
aws s3 ls "s3://serverless-destination-bucket/"
rm "test.txt"
