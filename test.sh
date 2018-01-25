#!/bin/bash

echo "Given an archive of multiple files to process"
aws s3 rm "s3://serverless-wordcount-hopper/" --recursive
aws s3 rm "s3://serverless-wordcount-result/" --recursive
aws s3 rm "s3://serverless-wordcount-archive/" --recursive
aws s3 cp "fragments-to-process-1K.tar.gz" "s3://serverless-wordcount-hopper/"

echo "When the archive is placed in a bucket"...
aws s3 ls "s3://serverless-wordcount-hopper/"

echo "Then the files in the archive are examined"
echo "and the words in the sentence fragments are counted in a dataframe"
echo "and the data frame is exported to a configured target folder"...
echo -n "." ; sleep 1 
echo -n "." ; sleep 1
echo -n "." ; sleep 1 
echo -n "." ; sleep 1
echo -n "." ; sleep 1
echo -n "." ; sleep 1
echo -n "." ; sleep 1
echo -n "." ; sleep 1
echo -n "." ; sleep 1

echo -n "." ; sleep 1
aws s3 ls "s3://serverless-wordcount-result/"

echo "and the processed archive is moved..."
aws s3 ls "s3://serverless-wordcount-hopper/" --summarize
echo "...to a configured bucket..."
aws s3 ls "s3://serverless-wordcount-archive/"