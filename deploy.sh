#!/bin/bash
# debug
# aws cloudformation describe-stack-events --stack-name serverless-wordcount-stack | grep "FAILED" -a2 | head -20

# Prepare source files for distribution
rm -rf "./dist"
mkdir -p "./dist"
echo "[install]" >> "./dist/setup.cfg"
echo "prefix= "  >> "./dist/setup.cfg"
cp "./lambda_wordcount_proxied.py" "./dist/."
cp "./lambda_wordcount_triggered.py" "./dist/."
cp "./task_wordcount.py" "./dist/."
cp "./utils_s3.py" "./dist/."
cp "./utils_transform.py" "./dist/."
cp "./utils_authorization.py" "./dist/."
cd "./dist"
python3 -m pip install PyPDF2 -t "."
python3 -m pip install timeout-decorator -t "."
cd ..

# Create API secret and embed in Serverless template
API_SECRET="$(uuidgen)"
sed -e 's/TEMPLATE_API_SECRET/'${API_SECRET?}'/g' "./serverless_wordcount_template.yaml" > "./serverless_wordcount.yaml"

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
rm "serverless_wordcount.yaml"
rm "serverless_wordcount_output.yaml"
rm -rf "./dist"
