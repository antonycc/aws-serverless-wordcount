# Serverless Word Count #

- [x] Given a PDF containing text
- [x] When the PDF is placed in a bucket
- [x] Then the PDF is transformed into fragments
- [x] and the words in the sentence fragments are counted
- [x] and the results are exported to a configured target folder
- [x] and the processed pdf is moved to a configured bucket.

TODO
- [ ] scripted build (or at least all scripts in python)
- [ ] pyenv
- [ ] project structure: https://docs.pytest.org/en/latest/goodpractices.html#goodpractices
- [ ] code style check
- [ ] deployed tests as pytest integration tests
- [ ] test coverage
- [ ] supply the Retry-After header in initial submission based on 20% lambda allocaton
- [ ] report on progress: https://www.adayinthelifeof.nl/2011/06/02/asynchronous-operations-in-rest/
- [ ] tests wait for iterations of estimated completion
- [ ] estimate completion time by extrapolating pages over time and expose in 404 resonses
- [ ] tests to use extrapolated completion after each check returning a 404
- [ ] mock writing to the local filesystem during tests (and copy filesystem tests to an integation suite)
- [ ] mock writing to s3 during tests (and copy s3 tests to an integration suite)

The output is a wordcount over all the fragments:
```json
{
   "a": 616,
   "aa": 9,
   "ab": 11,
   "abolish": 2,
   "abolished": 1,
   "abou": 1,
   "about": 32,
   "above": 4,
   "absent": 31,
#...truncated...
   "years": 3,
   "za": 13,
   "zb": 9,
   "zc": 22,
   "zcregistration": 1,
   "zd": 21,
   "zdregistration": 1,
   "ze": 2,
   "zeremoval": 1
}
```

The API requires an authorisation header with a discount JWT, built like this:
```bash
header |= "Authorization: Bearer " ++ <descriptor_base64> ++ "." ++ <signature>
signature |= hex( sha256( signing_string ) )
signing_string |= <secret> ++ <descriptor_base64>
descriptor_base64 = base64_encode( <descriptor> )
descriptor |= { "user": "<user>", "expires": "<expires>" } (Parsed as JSON)
user |= The name of the user for this token, e.g. local
expires |= Epox time in the future, e.g. 1518305033
secret |= any string for to generate, apply and forget, e.g. 587E99C4-72D4-4425-A7FB-BC3D9CAEEBFF
e.g.
Authorization: Bearer eyAidXNlciI6ICJsb2NhbCIsICJleHBpcmVzIjogIjE1MTgzMDQ0MDgiIH0=.b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16
```

Running
=======

Configure AWS
-------------

Install AWS CLI - See Amazon docs: https://docs.aws.amazon.com/cli/latest/userguide/installing.html

Also for macos, another option is Brew:
```bash
$ brew install awscli
Warning: awscli 1.14.30 is already installed
$
```

When installed, AWS CLI will report version information:
```bash
$ aws --version
aws-cli/1.14.29 Python/2.7.10 Darwin/17.3.0 botocore/1.8.33
$
```

Create a IAM user with the following Polices:
* Amazon: AWSLambdaFullAccess
* Amazon: AmazonS3FullAccess
* Amazon: AmazonAPIGatewayAdministrator
* Amazon: AWSCloudFormationReadOnlyAccess
* Custom: Custom policy for Cloud Formation and IAM actions (details below)

Configure the command line environment with your AWS credentials:
```bash
$ aws configure
AWS Access Key ID [None]: ********************
AWS Secret Access Key [None]: ****************************************
Default region name [None]: eu-central-1
Default output format [None]: json
$
```

Package and Deploy
------------------

Install Python libraries:
```bash
$ python3 -m pip install .
Processing /Users/antony/projects/aws-serverless-wordcount
Collecting PyPDF2>=1.26 (from AWS-Serverless-Wordcount==0.0.1)
Collecting timeout-decorator>=0.4.0 (from AWS-Serverless-Wordcount==0.0.1)
Installing collected packages: PyPDF2, timeout-decorator, AWS-Serverless-Wordcount
  Running setup.py install for AWS-Serverless-Wordcount ... done
Successfully installed AWS-Serverless-Wordcount-0.0.1 PyPDF2-1.26.0 timeout-decorator-0.4.0
$ 
```

Install https://docs.pytest.org/:
```bash
$ python3 -m pip install pytest
Requirement already satisfied: pytest in /usr/local/lib/python3.6/site-packages
Requirement already satisfied: six>=1.10.0 in /usr/local/lib/python3.6/site-packages (from pytest)
Requirement already satisfied: setuptools in /usr/local/lib/python3.6/site-packages (from pytest)
Requirement already satisfied: pluggy<0.7,>=0.5 in /usr/local/lib/python3.6/site-packages (from pytest)
Requirement already satisfied: py>=1.5.0 in /usr/local/lib/python3.6/site-packages (from pytest)
Requirement already satisfied: attrs>=17.2.0 in /usr/local/lib/python3.6/site-packages (from pytest)
$ 
```

Ensure unit tests pass:
```bash
$ pytest
=========================================================================================== test session starts ============================================================================================
platform darwin -- Python 3.6.4, pytest-3.4.0, py-1.5.2, pluggy-0.6.0
rootdir: /Users/antony/projects/aws-serverless-wordcount, inifile:
collected 21 items                                                                                                                                                                                         

test_unit_authorization.py ...........                                                                                                                                                               [ 52%]
test_unit_deployed_proxied.py .                                                                                                                                                                      [ 57%]
test_unit_deployed_triggered.py .                                                                                                                                                                    [ 61%]
test_unit_s3.py .....                                                                                                                                                                                [ 85%]
test_unit_transform.py ..                                                                                                                                                                            [ 95%]
test_unit_wordcount.py .                                                                                                                                                                             [100%]

======================================================================================== 21 passed in 2.94 seconds =========================================================================================
$ 
```

Choose a name and create an S3 deployment bucket:
```bash
$ aws s3 mb s3://serverless-wordcount-deploy
make_bucket: serverless-wordcount-deploy
$
```
The chosen name shall also need to be used in the next section.

Prepare source files for distribution:
```bash
$ rm -rf "./dist"
$ mkdir -p "./dist"
$ echo "[install]" >> "./dist/setup.cfg"
$ echo "prefix= "  >> "./dist/setup.cfg"
$ cp "./lambda_wordcount_proxied.py" "./dist/."
$ cp "./lambda_wordcount_triggered.py" "./dist/."
$ cp "./task_wordcount.py" "./dist/."
$ cp "./utils_s3.py" "./dist/."
$ cp "./utils_transform.py" "./dist/."
$ cp "./utils_authorization.py" "./dist/."
$ cd "./dist"
$ python3 -m pip install '.' -t '.'
Processing /Users/antony/projects/aws-serverless-wordcount/dist
Collecting PyPDF2>=1.26 (from AWS-Serverless-Wordcount==0.0.1)
Collecting timeout-decorator>=0.4.0 (from AWS-Serverless-Wordcount==0.0.1)
Installing collected packages: PyPDF2, timeout-decorator, AWS-Serverless-Wordcount
  Running setup.py install for AWS-Serverless-Wordcount ... done
Successfully installed AWS-Serverless-Wordcount-0.0.1 PyPDF2-1.26.0 timeout-decorator-0.4.0
$ cd ..
$ 
```

Create API secret and embed in Serverless template:
```bash
$ API_SECRET="$(uuidgen)"
$ sed -e 's/TEMPLATE_API_SECRET/'${API_SECRET?}'/g' "./serverless_wordcount_template.yaml" > "./serverless_wordcount.yaml"
$
```

Package AWS Lambda with Serverless template:
```bash
$ aws cloudformation package \
>   --template-file "serverless_wordcount.yaml" \
>   --output-template-file "serverless_wordcount_output.yaml" \
>   --s3-bucket "serverless-wordcount-deploy"

Uploading to 23fe95d8eb5abf3f9e19b593fc2b5bf5  252077 / 252077.0  (100.00%)
Successfully packaged artifacts and wrote output template to file serverless_wordcount_output.yaml.
Execute the following command to deploy the packaged template
aws cloudformation deploy --template-file /Users/antony/projects/aws-serverless-wordcount/serverless_wordcount_output.yaml --stack-name <YOUR STACK NAME>
$ 
```

Deploy AWS Lambda with Serverless template:
```bash
$ aws cloudformation deploy \
>    --template-file "serverless_wordcount_output.yaml" \
>    --stack-name "serverless-wordcount-stack" \
>    --capabilities CAPABILITY_IAM

Waiting for changeset to be created..
Waiting for stack create/update to complete
Successfully created/updated stack - serverless-wordcount-stack
$
```

Clean up:
```bash
$ rm "serverless_wordcount.yaml"
$ rm "serverless_wordcount_output.yaml"
$ rm -rf "./dist"
$
```

(included as deploy.sh)

Test
----

Querying deployment details:
```bash
$ API_SECRET=$(aws lambda get-function --function-name "ServerlessWordCountProxied" | jq --raw-output '.Configuration.Environment.Variables.ApiSecret')
$ REST_API_ID=$(aws apigateway get-rest-apis | jq --raw-output '.items[] | select(.name == "serverless-wordcount-stack") | .id')
$ REST_API_URL="https://${REST_API_ID?}.execute-api.eu-central-1.amazonaws.com/Prod"
$ 
```

Creating Authorization header:
```bash
$ API_USER="local"
$ API_TOKEN_EXPIRES="$(($(date +'%s + 3600')))"
$ API_TOKEN_DESCRIPTOR="{ \"user\": \"${API_USER?}\", \"expires\": \"${API_TOKEN_EXPIRES?}\" }"
$ API_AUTHORIZATION_USER=$(echo -n "${API_TOKEN_DESCRIPTOR?}" | base64)
$ API_AUTHORIZATION_SIGNATURE=$(echo -n "${API_SECRET?}${API_AUTHORIZATION_USER?}" | openssl sha -sha256)
$ API_AUTHORIZATION="${API_AUTHORIZATION_USER?}.${API_AUTHORIZATION_SIGNATURE?}"
$ AUTHORIZATION_HEADER="Authorization: Bearer ${API_AUTHORIZATION?}"
$ 
```

API Test healthcheck:
```bash
$ curl --silent \
>    --request GET "${REST_API_URL?}/health" \
>    --header "${AUTHORIZATION_HEADER?}" \
>    | jq '.'
{
  "s3": {
    "serverless-wordcount-hopper": "ok",
    "serverless-wordcount-result": "ok",
    "health_check_passed": true
  }
}
$
````

Given a PDF containing text:
```bash
$ aws s3 rm "s3://serverless-wordcount-hopper/" --recursive
$ aws s3 rm "s3://serverless-wordcount-result/" --recursive
$ aws s3 rm "s3://serverless-wordcount-archive/" --recursive
$
```

When the PDF is asynronously submitted:
```bash
Antonys-MacBook-Pro:aws-serverless-wordcount antony$ curl --include \
>   --request POST "${REST_API_URL?}/wordcount" \
>   --header "${AUTHORIZATION_HEADER?}" \
>   --data @"./${FILENAME?}.base64" 
HTTP/2 202 
content-type: application/json
content-length: 0
date: Sat, 10 Feb 2018 21:48:45 GMT
x-amzn-requestid: 2afda6ac-0eac-11e8-b776-ffc93935d8f7
location: /wordcount/25758f5d-93b8-4827-bbe4-82ab2566ce24.pdf
x-amzn-trace-id: sampled=0;root=1-5a7f68bd-ab4b03769277326ff49bfa4b
x-cache: Miss from cloudfront
via: 1.1 eeee1e9393059101448ec0a1c21a3018.cloudfront.net (CloudFront)
x-amz-cf-id: Y2_dN4CxHsnlBbs2nrfV7EQH0o5fC4gYREAQNU948MAmgbfiNfI-hA==

$ RESOURCE_PATH="/wordcount/25758f5d-93b8-4827-bbe4-82ab2566ce24.pdf"
$
```
(Resource path is populated using the value of the Location header)

We can poll until the resource is ready:
```bash
$ curl --include \
>   --request GET "${REST_API_URL?}/${RESOURCE_PATH?}" \
>   --header "${AUTHORIZATION_HEADER?}"
HTTP/2 404 
content-type: application/json
content-length: 0
date: Sat, 10 Feb 2018 21:59:22 GMT
x-amzn-requestid: a69d5572-0ead-11e8-b1a7-21917ed4ebc8
x-amzn-trace-id: sampled=0;root=1-5a7f6b3a-859333020d03ee8c7e308e4b
x-cache: Error from cloudfront
via: 1.1 87510893413a5a70f5cf33b727e70ad8.cloudfront.net (CloudFront)
x-amz-cf-id: wlv_PX5E9-mLHkYnMTSqbVe-8adXgwm3MDP1H07ZZAbdwCj5Pb4rmA==

$ 
$ curl --include \
>   --request GET "${REST_API_URL?}/${RESOURCE_PATH?}" \
>   --header "${AUTHORIZATION_HEADER?}"
HTTP/2 404 
content-type: application/json
content-length: 0
date: Sat, 10 Feb 2018 21:59:22 GMT
x-amzn-requestid: a69d5572-0ead-11e8-b1a7-21917ed4ebc8
x-amzn-trace-id: sampled=0;root=1-5a7f6b3a-859333020d03ee8c7e308e4b
x-cache: Error from cloudfront
via: 1.1 87510893413a5a70f5cf33b727e70ad8.cloudfront.net (CloudFront)
x-amz-cf-id: wlv_PX5E9-mLHkYnMTSqbVe-8adXgwm3MDP1H07ZZAbdwCj5Pb4rmA==

$ 
```

Then the PDF is transformed into fragments
and the words in the sentence fragments are counted
and the results are exported to a configured target folder:
```bash
$ curl \
>   --request GET "${REST_API_URL?}/${RESOURCE_PATH?}" \
>   --header "${AUTHORIZATION_HEADER?}" \
>   --output "./${FILENAME?}-async-result.json"
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 16771  100 16771    0     0  28089      0 --:--:-- --:--:-- --:--:-- 28045
$ cat "./${FILENAME?}-async-result.json" | jq '.' | head -10
{
   "a": 616,
   "aa": 9,
   "ab": 11,
   "abolish": 2,
   "abolished": 1,
   "abou": 1,
   "about": 32,
   "above": 4,
   "absent": 31,
$ cat "./${FILENAME?}-async-result.json" | jq '.' | tail -10
   "years": 3,
   "za": 13,
   "zb": 9,
   "zc": 22,
   "zcregistration": 1,
   "zd": 21,
   "zdregistration": 1,
   "ze": 2,
   "zeremoval": 1
}

```

and the processed pdf is moved to a configured bucket.
```bash
$ aws s3 ls "s3://serverless-wordcount-hopper/" --summarize

Total Objects: 0
   Total Size: 0  
$ aws s3 ls "s3://serverless-wordcount-result/"
2018-02-10 22:59:31      20418 4b124fc8-3bae-4cd3-9a9d-a18343ce8527.pdf-result.json
2018-02-10 22:59:31      99394 4b124fc8-3bae-4cd3-9a9d-a18343ce8527.pdf-result.json.descriptor.json
$ aws s3 ls "s3://serverless-wordcount-archive/"
2018-02-10 22:59:31     357161 4b124fc8-3bae-4cd3-9a9d-a18343ce8527.pdf
$
```

Observe
-------

The CloudWatch console shows serveral log events throughout the several seconds of execution:
```
START RequestId: 9f5985a7-0eaf-11e8-96c8-537d85c8e846 Version: $LATEST
[INFO]  2018-02-10T22:13:29.581Z  9f5985a7-0eaf-11e8-96c8-537d85c8e846  Checking authorization_header=[Bearer eyAidXNlciI6ICJsb2NhbCIsICJleHBpcmVzIjogIjE1MTgzMDQ0MDgiIH0=.b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:29.581Z  9f5985a7-0eaf-11e8-96c8-537d85c8e846  generated_signature=[b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:29.581Z  9f5985a7-0eaf-11e8-96c8-537d85c8e846  Accepted bearer token for: local (expires:1518304408)
[INFO]  2018-02-10T22:13:29.584Z  9f5985a7-0eaf-11e8-96c8-537d85c8e846  Starting new HTTPS connection (1): s3.eu-central-1.amazonaws.com
END RequestId: 9f5985a7-0eaf-11e8-96c8-537d85c8e846
REPORT RequestId: 9f5985a7-0eaf-11e8-96c8-537d85c8e846  Duration: 224.05 ms Billed Duration: 300 ms Memory Size: 128 MB Max Memory Used: 37 MB  
START RequestId: a3966bee-0eaf-11e8-9c7d-d38f153cb83b Version: $LATEST
[INFO]  2018-02-10T22:13:36.208Z  a3966bee-0eaf-11e8-9c7d-d38f153cb83b  Checking authorization_header=[Bearer eyAidXNlciI6ICJsb2NhbCIsICJleHBpcmVzIjogIjE1MTgzMDQ0MDgiIH0=.b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:36.209Z  a3966bee-0eaf-11e8-9c7d-d38f153cb83b  generated_signature=[b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:36.209Z  a3966bee-0eaf-11e8-9c7d-d38f153cb83b  Accepted bearer token for: local (expires:1518304408)
[INFO]  2018-02-10T22:13:36.223Z  a3966bee-0eaf-11e8-9c7d-d38f153cb83b  Asynchronous processing...
[INFO]  2018-02-10T22:13:36.243Z  a3966bee-0eaf-11e8-9c7d-d38f153cb83b  Uploading /tmp/72a46e82-9577-488a-815a-fd13d7e64d33 to bucket serverless-wordcount-hopper using key 7ed160a7-3eca-4eb1-8a30-655b33408f0e.pdf
[INFO]  2018-02-10T22:13:36.266Z  a3966bee-0eaf-11e8-9c7d-d38f153cb83b  Resetting dropped connection: s3.eu-central-1.amazonaws.com
END RequestId: a3966bee-0eaf-11e8-9c7d-d38f153cb83b
REPORT RequestId: a3966bee-0eaf-11e8-9c7d-d38f153cb83b  Duration: 290.60 ms Billed Duration: 300 ms Memory Size: 128 MB Max Memory Used: 37 MB  
START RequestId: a3ed3ea0-0eaf-11e8-875e-8bf834e8b134 Version: $LATEST
[INFO]  2018-02-10T22:13:36.775Z  a3ed3ea0-0eaf-11e8-875e-8bf834e8b134  Checking authorization_header=[Bearer eyAidXNlciI6ICJsb2NhbCIsICJleHBpcmVzIjogIjE1MTgzMDQ0MDgiIH0=.b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:36.775Z  a3ed3ea0-0eaf-11e8-875e-8bf834e8b134  generated_signature=[b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:36.775Z  a3ed3ea0-0eaf-11e8-875e-8bf834e8b134  Accepted bearer token for: local (expires:1518304408)
[INFO]  2018-02-10T22:13:36.792Z  a3ed3ea0-0eaf-11e8-875e-8bf834e8b134  Did not find s3://serverless-wordcount-result/7ed160a7-3eca-4eb1-8a30-655b33408f0e.pdf-result.json
END RequestId: a3ed3ea0-0eaf-11e8-875e-8bf834e8b134
REPORT RequestId: a3ed3ea0-0eaf-11e8-875e-8bf834e8b134  Duration: 17.15 ms  Billed Duration: 100 ms Memory Size: 128 MB Max Memory Used: 37 MB  
START RequestId: a410308a-0eaf-11e8-b680-c53ac127f2af Version: $LATEST
[INFO]  2018-02-10T22:13:36.988Z  a410308a-0eaf-11e8-b680-c53ac127f2af  Checking authorization_header=[Bearer eyAidXNlciI6ICJsb2NhbCIsICJleHBpcmVzIjogIjE1MTgzMDQ0MDgiIH0=.b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:36.988Z  a410308a-0eaf-11e8-b680-c53ac127f2af  generated_signature=[b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:36.988Z  a410308a-0eaf-11e8-b680-c53ac127f2af  Accepted bearer token for: local (expires:1518304408)
[INFO]  2018-02-10T22:13:37.4Z  a410308a-0eaf-11e8-b680-c53ac127f2af  Did not find s3://serverless-wordcount-result/7ed160a7-3eca-4eb1-8a30-655b33408f0e.pdf-result.json
END RequestId: a410308a-0eaf-11e8-b680-c53ac127f2af
REPORT RequestId: a410308a-0eaf-11e8-b680-c53ac127f2af  Duration: 24.36 ms  Billed Duration: 100 ms Memory Size: 128 MB Max Memory Used: 37 MB  
START RequestId: a69813bc-0eaf-11e8-a0b8-85c429cbf101 Version: $LATEST
[INFO]  2018-02-10T22:13:41.234Z  a69813bc-0eaf-11e8-a0b8-85c429cbf101  Checking authorization_header=[Bearer eyAidXNlciI6ICJsb2NhbCIsICJleHBpcmVzIjogIjE1MTgzMDQ0MDgiIH0=.b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:41.234Z  a69813bc-0eaf-11e8-a0b8-85c429cbf101  generated_signature=[b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:41.234Z  a69813bc-0eaf-11e8-a0b8-85c429cbf101  Accepted bearer token for: local (expires:1518304408)
[INFO]  2018-02-10T22:13:41.247Z  a69813bc-0eaf-11e8-a0b8-85c429cbf101  Did not find s3://serverless-wordcount-result/7ed160a7-3eca-4eb1-8a30-655b33408f0e.pdf-result.json
END RequestId: a69813bc-0eaf-11e8-a0b8-85c429cbf101
REPORT RequestId: a69813bc-0eaf-11e8-a0b8-85c429cbf101  Duration: 29.20 ms  Billed Duration: 100 ms Memory Size: 128 MB Max Memory Used: 37 MB  
START RequestId: a9246413-0eaf-11e8-807d-a70fd559e5e7 Version: $LATEST
[INFO]  2018-02-10T22:13:45.509Z  a9246413-0eaf-11e8-807d-a70fd559e5e7  Checking authorization_header=[Bearer eyAidXNlciI6ICJsb2NhbCIsICJleHBpcmVzIjogIjE1MTgzMDQ0MDgiIH0=.b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:45.509Z  a9246413-0eaf-11e8-807d-a70fd559e5e7  generated_signature=[b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:45.509Z  a9246413-0eaf-11e8-807d-a70fd559e5e7  Accepted bearer token for: local (expires:1518304408)
[INFO]  2018-02-10T22:13:45.525Z  a9246413-0eaf-11e8-807d-a70fd559e5e7  Did not find s3://serverless-wordcount-result/7ed160a7-3eca-4eb1-8a30-655b33408f0e.pdf-result.json
END RequestId: a9246413-0eaf-11e8-807d-a70fd559e5e7
REPORT RequestId: a9246413-0eaf-11e8-807d-a70fd559e5e7  Duration: 17.24 ms  Billed Duration: 100 ms Memory Size: 128 MB Max Memory Used: 37 MB  
START RequestId: abadce2e-0eaf-11e8-bfb4-87b8973e9259 Version: $LATEST
[INFO]  2018-02-10T22:13:49.765Z  abadce2e-0eaf-11e8-bfb4-87b8973e9259  Checking authorization_header=[Bearer eyAidXNlciI6ICJsb2NhbCIsICJleHBpcmVzIjogIjE1MTgzMDQ0MDgiIH0=.b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:49.765Z  abadce2e-0eaf-11e8-bfb4-87b8973e9259  generated_signature=[b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:49.765Z  abadce2e-0eaf-11e8-bfb4-87b8973e9259  Accepted bearer token for: local (expires:1518304408)
[INFO]  2018-02-10T22:13:49.794Z  abadce2e-0eaf-11e8-bfb4-87b8973e9259  Did not find s3://serverless-wordcount-result/7ed160a7-3eca-4eb1-8a30-655b33408f0e.pdf-result.json
END RequestId: abadce2e-0eaf-11e8-bfb4-87b8973e9259
REPORT RequestId: abadce2e-0eaf-11e8-bfb4-87b8973e9259  Duration: 29.83 ms  Billed Duration: 100 ms Memory Size: 128 MB Max Memory Used: 37 MB  
START RequestId: ae3ba457-0eaf-11e8-a367-690339b9bc41 Version: $LATEST
[INFO]  2018-02-10T22:13:54.50Z ae3ba457-0eaf-11e8-a367-690339b9bc41  Checking authorization_header=[Bearer eyAidXNlciI6ICJsb2NhbCIsICJleHBpcmVzIjogIjE1MTgzMDQ0MDgiIH0=.b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:54.50Z ae3ba457-0eaf-11e8-a367-690339b9bc41  generated_signature=[b3c33e0315fa302906cadb1066678b8936f68ebccf6a04875fd6dbfd27030f16]
[INFO]  2018-02-10T22:13:54.50Z ae3ba457-0eaf-11e8-a367-690339b9bc41  Accepted bearer token for: local (expires:1518304408)
[INFO]  2018-02-10T22:13:54.110Z  ae3ba457-0eaf-11e8-a367-690339b9bc41  Resource Exists s3://serverless-wordcount-result/7ed160a7-3eca-4eb1-8a30-655b33408f0e.pdf-result.json
END RequestId: ae3ba457-0eaf-11e8-a367-690339b9bc41
REPORT RequestId: ae3ba457-0eaf-11e8-a367-690339b9bc41  Duration: 173.45 ms Billed Duration: 200 ms Memory Size: 128 MB Max Memory Used: 38 MB  
Feedback
English (US)
Terms of UsePrivacy Policy© 2008 - 2018, Amazon Web Services, Inc. or its affiliates. All rights reserved.

```

(included as test_deployed_proxied_primary.sh)

Cloud Formation Custom Policy
=============================

This custom policy for Cloud Formation and IAM actions was generated with the Visual Editor:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "cloudformation:CancelUpdateStack",
                "cloudformation:CreateStack",
                "cloudformation:DeleteStack",
                "cloudformation:SignalResource",
                "cloudformation:UpdateStack",
                "cloudformation:UpdateTerminationProtection",
                "cloudformation:CreateChangeSet",
                "cloudformation:ExecuteChangeSet",
                "cloudformation:DeleteChangeSet",
                "cloudformation:ContinueUpdateRollback"
            ],
            "Resource": [
                "arn:aws:cloudformation:*:*:stack/*/*",
                "arn:aws:cloudformation:*:*:transform/Serverless-2016-10-31"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "cloudformation:CreateUploadBucket",
                "iam:CreateRole",
                "iam:DetachRolePolicy",
                "iam:DeleteRole",
                "iam:AttachRolePolicy",
                "cloudformation:ValidateTemplate"
            ],
            "Resource": "*"
        }
    ]
}
```