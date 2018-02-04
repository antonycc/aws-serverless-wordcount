#!/bin/bash

REST_API_ID=$(aws apigateway get-rest-apis | jq --raw-output '.items[] | select(.name == "serverless-wordcount-stack") | .id')
REST_API_URL="https://${REST_API_ID?}.execute-api.eu-central-1.amazonaws.com/Prod/wordcount"

echo "API Test expect HTTP 401"
AUTHORIZATION_HEADER="Authorization: Bearer ${API_AUTHORIZATION?}X"
REST_API_TEST_CMD="curl --include --silent --request GET \"${REST_API_URL?}\" --header "${AUTHORIZATION_HEADER?}" | head ; echo"
echo "${REST_API_TEST_CMD?}"
eval "${REST_API_TEST_CMD?}"

echo "API Test expect HTTP 200"
AUTHORIZATION_HEADER="Authorization: Bearer ${API_AUTHORIZATION?}"
REST_API_TEST_CMD="curl --include --silent --request GET \"${REST_API_URL?}\" --header "${AUTHORIZATION_HEADER?}" | head ; echo"
echo "${REST_API_TEST_CMD?}"
eval "${REST_API_TEST_CMD?}"

#echo "Given a PDF containing text"
#aws s3 rm "s3://serverless-wordcount-hopper/" --recursive
#aws s3 rm "s3://serverless-wordcount-result/" --recursive
#aws s3 rm "s3://serverless-wordcount-archive/" --recursive

# API Test
#echo "When the PDF is placed in a bucket..."
#FILE="./polycode.co.uk-mug.jpeg"
#base64 "${FILE?}" > "${FILE?}.base64"
#REST_API_TEST_CMD="curl --include --silent --request POST \"${REST_API_URL?}\" --header "${AUTHORIZATION_HEADER?}" --data @\"${FILE?}.base64\" ; echo"
#echo "${REST_API_TEST_CMD?}"
#eval "${REST_API_TEST_CMD?}"
#aws s3 ls "s3://serverless-wordcount-hopper/"

#echo "Then the PDF is transformed into fragments"
#echo "and the words in the sentence fragments are counted"
#echo "and the results are exported to a configured target folder"
#echo "and the processed pdf is moved to a configured bucket..."
#echo -n "5" ; sleep 1 
#echo -n "." ; sleep 1
#echo -n "." ; sleep 1 
#echo -n "." ; sleep 1
#echo -n "4" ; sleep 1
#echo -n "." ; sleep 1
#echo -n "." ; sleep 1
#echo -n "." ; sleep 1
#echo -n "3" ; sleep 1
#echo -n "." ; sleep 1
#echo -n "." ; sleep 1 
#echo -n "." ; sleep 1
#echo -n "2" ; sleep 1 
#echo -n "." ; sleep 1
#echo -n "." ; sleep 1
#echo -n "." ; sleep 1
#echo -n "1" ; sleep 1
#echo -n "." ; sleep 1
#echo -n "." ; sleep 1
#echo -n "." ; sleep 1 ; echo
#aws s3 ls "s3://serverless-wordcount-result/"

#echo "and the processed archive is moved..."
#aws s3 ls "s3://serverless-wordcount-hopper/" --summarize
#echo "...to a configured bucket..."
#aws s3 ls "s3://serverless-wordcount-archive/"