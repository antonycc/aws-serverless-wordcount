#!/bin/bash

echo "Given a PDF containing text"
aws s3 rm "s3://serverless-wordcount-hopper/" --recursive
aws s3 rm "s3://serverless-wordcount-result/" --recursive
aws s3 rm "s3://serverless-wordcount-archive/" --recursive
aws s3 cp "ukpga_20100013_en.pdf" "s3://serverless-wordcount-hopper/"

echo "When the PDF is placed in a bucket..."
aws s3 ls "s3://serverless-wordcount-hopper/"

echo "Then the PDF is transformed into fragments"
echo "and the words in the sentence fragments are counted"
echo "and the results are exported to a configured target folder"
echo "and the processed pdf is moved to a configured bucket..."
echo -n "5" ; sleep 1 
echo -n "." ; sleep 1
echo -n "." ; sleep 1 
echo -n "." ; sleep 1
echo -n "4" ; sleep 1
echo -n "." ; sleep 1
echo -n "." ; sleep 1
echo -n "." ; sleep 1
echo -n "3" ; sleep 1
echo -n "." ; sleep 1
echo -n "." ; sleep 1 
echo -n "." ; sleep 1
echo -n "2" ; sleep 1 
echo -n "." ; sleep 1
echo -n "." ; sleep 1
echo -n "." ; sleep 1
echo -n "1" ; sleep 1
echo -n "." ; sleep 1
echo -n "." ; sleep 1
echo -n "." ; sleep 1 ; echo
aws s3 ls "s3://serverless-wordcount-result/"

echo "and the processed archive is moved..."
aws s3 ls "s3://serverless-wordcount-hopper/" --summarize
echo "...to a configured bucket..."
aws s3 ls "s3://serverless-wordcount-archive/"