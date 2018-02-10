#!/bin/bash
# Exercise the deployed service proxied through the API Gateway

echo "Querying deployment details"
API_SECRET=$(aws lambda get-function --function-name "ServerlessWordCountProxied" | jq --raw-output '.Configuration.Environment.Variables.ApiSecret')
REST_API_ID=$(aws apigateway get-rest-apis | jq --raw-output '.items[] | select(.name == "serverless-wordcount-stack") | .id')
REST_API_URL="https://${REST_API_ID?}.execute-api.eu-central-1.amazonaws.com/Prod"
echo

echo "Creating Authorization header"
API_USER="local"
API_TOKEN_EXPIRES="$(($(date +'%s + 3600')))"
API_TOKEN_DESCRIPTOR="{ \"user\": \"${API_USER?}\", \"expires\": \"${API_TOKEN_EXPIRES?}\" }"
API_AUTHORIZATION_USER=$(echo -n "${API_TOKEN_DESCRIPTOR?}" | base64)
API_AUTHORIZATION_SIGNATURE=$(echo -n "${API_SECRET?}${API_AUTHORIZATION_USER?}" | openssl sha -sha256)
API_AUTHORIZATION="${API_AUTHORIZATION_USER?}.${API_AUTHORIZATION_SIGNATURE?}"
echo "API_SECRET=\"${API_SECRET?}\""
echo "API_AUTHORIZATION=\"${API_AUTHORIZATION?}\""
echo

echo "API Test healthcheck expect HTTP 200"
AUTHORIZATION_HEADER="Authorization: Bearer ${API_AUTHORIZATION?}"
REST_API_TEST_CMD="curl --include --silent --request GET \"${REST_API_URL?}/health\" --header \"${AUTHORIZATION_HEADER?}\" ; echo"
echo "${REST_API_TEST_CMD?}"
eval "${REST_API_TEST_CMD?}"
echo

echo "Given a PDF containing text"
aws s3 rm "s3://serverless-wordcount-hopper/" --recursive
aws s3 rm "s3://serverless-wordcount-result/" --recursive
aws s3 rm "s3://serverless-wordcount-archive/" --recursive

echo "When the PDF is asynronously submitted..."
FILENAME="ukpga_20100013_en.pdf"
base64 "./${FILENAME?}" > "./${FILENAME?}.base64"
#REST_API_TEST_CMD="curl --include --silent --request POST \"${REST_API_URL?}/wordcount?filename=$(uuidgen).pdf\" --header \"${AUTHORIZATION_HEADER?}\" --data @\"./${FILENAME?}.base64\" --output \"./output.txt\" ; echo"
REST_API_TEST_CMD="curl --include --silent --request POST \"${REST_API_URL?}/wordcount\" --header \"${AUTHORIZATION_HEADER?}\" --data @\"./${FILENAME?}.base64\" --output \"./output.txt\" ; echo"
echo "${REST_API_TEST_CMD?}"
eval "${REST_API_TEST_CMD?}"
dos2unix "./output.txt"
RESOURCE_PATH=$( cat "./output.txt" | grep -i "location: " | head -1 | sed -e 's/location: \///')
echo "RESOURCE_PATH=${RESOURCE_PATH?}"
rm -f "./output.txt"
echo
curl --include \
  --request GET "${REST_API_URL?}/${RESOURCE_PATH?}" \
  --header "${AUTHORIZATION_HEADER?}"


echo "We can poll until..."
echo "Then the PDF is transformed into fragments"
echo "and the words in the sentence fragments are counted"
echo "and the results are exported to a configured target folder"
echo "and the processed pdf is moved to a configured bucket..."
rm -f "./${FILENAME?}-async-result.json"
REST_API_TEST_CMD="curl --silent --request GET \"${REST_API_URL?}/${RESOURCE_PATH?}\" --header \"${AUTHORIZATION_HEADER?}\" --output \"./${FILENAME?}-async-result.json\""
eval "${REST_API_TEST_CMD?}"
while [ ! -s "./${FILENAME?}-async-result.json" ]
do
   echo -n "." ; sleep 1
   echo -n "." ; sleep 1
   echo -n "." ; sleep 1
   echo -n "." ; sleep 1 ; echo
   echo "${REST_API_TEST_CMD?}"
   eval "${REST_API_TEST_CMD?}"
done
cat "./${FILENAME?}-async-result.json" | jq '.' | head -10
echo "...truncated..."
cat "./${FILENAME?}-async-result.json" | jq '.' | tail -10

