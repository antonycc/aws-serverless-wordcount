#!/bin/bash

echo "Serverless test file" > "test.txt"
aws s3 cp "test.txt" "s3://serverless-source-bucket/test.txt"

echo -n "." ; sleep 1 
echo -n "." ; sleep 1
echo -n "." ; sleep 1 
echo -n "." ; sleep 1
echo -n "." ; sleep 1

aws s3 ls "s3://serverless-destination-bucket/"

rm "test.txt"
