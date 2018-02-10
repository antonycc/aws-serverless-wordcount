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

echo "API Test with invalid token expect HTTP 401"
AUTHORIZATION_HEADER="Authorization: Bearer ${API_AUTHORIZATION?}FAIL"
REST_API_TEST_CMD="curl --include --silent --request GET \"${REST_API_URL?}/wordcount/health\" --header \"${AUTHORIZATION_HEADER?}\" ; echo"
echo "${REST_API_TEST_CMD?}"
eval "${REST_API_TEST_CMD?}"
echo

echo "API Test with missing resource HTTP 404"
RESOURCE_KEY="$(uuidgen)"
AUTHORIZATION_HEADER="Authorization: Bearer ${API_AUTHORIZATION?}"
REST_API_TEST_CMD="curl --include --silent --request GET \"${REST_API_URL?}/wordcount/${RESOURCE_KEY?}\" --header \"${AUTHORIZATION_HEADER?}\" ; echo"
echo "${REST_API_TEST_CMD?}"
eval "${REST_API_TEST_CMD?}"
echo

echo "API Test with found resource HTTP 200"
RESOURCE_KEY="ukpga_20100013_en.pdf"
AUTHORIZATION_HEADER="Authorization: Bearer ${API_AUTHORIZATION?}"
REST_API_TEST_CMD="curl --silent --request GET \"${REST_API_URL?}/wordcount/${RESOURCE_KEY?}\" --header \"${AUTHORIZATION_HEADER?}\" --output \"./${RESOURCE_KEY?}-fake-result.json\" ; echo"
aws s3 rm "s3://serverless-wordcount-result/" --recursive
aws s3 cp "./${RESOURCE_KEY?}-result.json" "s3://serverless-wordcount-result/"
echo "${REST_API_TEST_CMD?}"
eval "${REST_API_TEST_CMD?}"
cat "./${RESOURCE_KEY?}-fake-result.json" | jq '.' | head -10
echo "...truncated..."
cat "./${RESOURCE_KEY?}-fake-result.json" | jq '.' | tail -10
echo

echo "When the PDF is synronously sent..."
FILENAME="ukpga_20100013_en.pdf"
base64 "./${FILENAME?}" > "./${FILENAME?}.base64"
REST_API_TEST_CMD="curl --request POST \"${REST_API_URL?}/wordcount?is_synchronous=true\" --header \"${AUTHORIZATION_HEADER?}\" --data @\"./${FILENAME?}.base64\" --output \"./${FILENAME?}-sync-result.json\" | head -20 ; echo"
echo "${REST_API_TEST_CMD?}"
eval "${REST_API_TEST_CMD?}"
cat "./${FILENAME?}-sync-result.json" | jq '.' | head -10
echo "...truncated..."
cat "./${FILENAME?}-sync-result.json" | jq '.' | tail -10
rm "./${FILENAME?}.base64"

