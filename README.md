# Serverless Word Count #

- [x] Given a PDF containing text
- [x] When the PDF is placed in a bucket
- [x] Then the PDF is transformed into fragments
- [x] and the words in the sentence fragments are counted
- [x] and the results are exported to a configured target folder
- [x] and the processed pdf is moved to a configured bucket.

TODO
- [ ] Get sync job to generate response
- [ ] In sync job, pass the bytes, return the result, don't write files at all

The descriptor contains basic metadata and sentence fragments from the document:
```json
{
   "downloadedFileAt": "2017-06-25T00:16:00.304541",
   "downloadedFilename": "4d52dafd817564fcb4f226472d8897637c4b8ec389a9cb7294959370443011b3.pdf",
   "timestamp": "2017-06-25T00:01:07Z+0100",
   "type": "pdf_descriptor",
   "fragments": [
      "para graph (1) may include provision (a)conferring functions on registration office rs.",
      "or local or public authorities.",
      "to enable applicatio ns to be made in a particular manner.",
      "(b)conferring other functions on registration officers.",
      "(c)conferring functions on the Electoral Commission.",
      "Electoral Registration and Administration Act 2013 (c."
   ]
}
```

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

Running
=======

Install AWS CLI
---------------

See Amazon docs: https://docs.aws.amazon.com/cli/latest/userguide/installing.html

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

Configure Python libraries
--------------------------

https://github.com/mstamy2/PyPDF2
```bash
$ python3 -m pip install PyPDF2
Collecting PyPDF2
Installing collected packages: PyPDF2
Successfully installed PyPDF2-1.26.0
$ 
```

https://pypi.python.org/pypi/timeout-decorator
```bash
$ python3 -m pip install timeout-decorator
Collecting timeout-decorator
Installing collected packages: timeout-decorator
Successfully installed timeout-decorator-0.4.0
$ 
```

Configure AWS
-------------

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
$ cp "./lambda_wordcount.py" "./dist/."
$ cp "./task_wordcount.py" "./dist/."
$ cd "./dist"
$ python3 -m pip install PyPDF2 -t "."
Collecting PyPDF2
Installing collected packages: PyPDF2
Successfully installed PyPDF2-1.26.0
$ python3 -m pip install timeout-decorator -t "."
Collecting timeout-decorator
Installing collected packages: timeout-decorator
Successfully installed timeout-decorator-0.4.0
$ cd ..
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
$ rm -rf "./dist"
$
```

(included as deploy.sh)

Test
----

Given a PDF containing text
```bash
$ aws s3 rm "s3://serverless-wordcount-hopper/" --recursive
$ aws s3 rm "s3://serverless-wordcount-result/" --recursive
$ aws s3 rm "s3://serverless-wordcount-archive/" --recursive
$ aws s3 cp "ukpga_20100013_en.pdf" "s3://serverless-wordcount-hopper/"
upload: ./ukpga_20100013_en.pdf to s3://serverless-wordcount-hopper/ukpga_20100013_en.pdf
$
```

When the PDF is placed in a bucket
```bash
$ aws s3 ls "s3://serverless-wordcount-hopper/"
2018-02-01 19:43:47     357161 ukpga_20100013_en.pdf
$
```

Then the PDF is transformed into fragments
and the words in the sentence fragments are counted
and the results are exported to a configured target folder
```bash
$ aws s3 ls "s3://serverless-wordcount-result/"
2018-02-01 19:44:09      20418 ukpga_20100013_en.pdf-result.json
2018-02-01 19:44:09      99375 ukpga_20100013_en.pdf-result.json.descriptor.json
$ aws s3 cp "s3://serverless-wordcount-result/ukpga_20100013_en.pdf-result.json" "ukpga_20100013_en.pdf-result.json"
download: s3://serverless-wordcount-result/ukpga_20100013_en.pdf-result.json to ./ukpga_20100013_en.pdf-result.json
$ head "./ukpga_20100013_en.pdf-result.json"
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
$ tail ukpga_20100013_en.pdf-result.json
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
$
```

and the processed pdf is moved to a configured bucket.
```bash
$ aws s3 ls "s3://serverless-wordcount-hopper/" --summarize

Total Objects: 0
   Total Size: 0  
$ aws s3 ls "s3://serverless-wordcount-archive/"
2018-02-01 19:44:09     357161 ukpga_20100013_en.pdf
$
```

Observe
-------

The CloudWatch console shows serveral log events throughout the several seconds of execution:
```
[INFO]  2018-02-01T18:49:32.768Z  Found credentials in environment variables.
START RequestId: a3ebad7b-0780-11e8-9747-d58c273a1af5 Version: $LATEST
[INFO]  2018-02-01T18:49:32.815Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Processing all records...
[INFO]  2018-02-01T18:49:32.838Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Starting new HTTPS connection (1): s3.eu-central-1.amazonaws.com
[INFO]  2018-02-01T18:49:33.176Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Opening PDF [/tmp/ukpga_20100013_en.pdf]
[INFO]  2018-02-01T18:49:33.855Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 0
[INFO]  2018-02-01T18:49:33.916Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 1
[INFO]  2018-02-01T18:49:33.916Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 2
[INFO]  2018-02-01T18:49:34.176Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 3
[INFO]  2018-02-01T18:49:34.376Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 4
[INFO]  2018-02-01T18:49:34.639Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 5
[INFO]  2018-02-01T18:49:35.118Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 6
[INFO]  2018-02-01T18:49:35.577Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 7
[INFO]  2018-02-01T18:49:35.997Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 8
[INFO]  2018-02-01T18:49:36.418Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 9
[INFO]  2018-02-01T18:49:36.936Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 10
[INFO]  2018-02-01T18:49:37.416Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 11
[INFO]  2018-02-01T18:49:37.936Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 12
[INFO]  2018-02-01T18:49:38.357Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 13
[INFO]  2018-02-01T18:49:38.778Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 14
[INFO]  2018-02-01T18:49:39.256Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 15
[INFO]  2018-02-01T18:49:39.718Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 16
[INFO]  2018-02-01T18:49:40.138Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 17
[INFO]  2018-02-01T18:49:40.499Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 18
[INFO]  2018-02-01T18:49:40.939Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 19
[INFO]  2018-02-01T18:49:41.357Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 20
[INFO]  2018-02-01T18:49:41.778Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 21
[INFO]  2018-02-01T18:49:42.256Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 22
[INFO]  2018-02-01T18:49:42.676Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 23
[INFO]  2018-02-01T18:49:43.39Z a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 24
[INFO]  2018-02-01T18:49:43.457Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 25
[INFO]  2018-02-01T18:49:43.879Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 26
[INFO]  2018-02-01T18:49:44.296Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 27
[INFO]  2018-02-01T18:49:44.716Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 28
[INFO]  2018-02-01T18:49:45.137Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 29
[INFO]  2018-02-01T18:49:45.596Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 30
[INFO]  2018-02-01T18:49:45.977Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 31
[INFO]  2018-02-01T18:49:46.495Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 32
[INFO]  2018-02-01T18:49:46.958Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 33
[INFO]  2018-02-01T18:49:47.496Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 34
[INFO]  2018-02-01T18:49:48.37Z a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 35
[INFO]  2018-02-01T18:49:48.579Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 36
[INFO]  2018-02-01T18:49:49.257Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 37
[INFO]  2018-02-01T18:49:49.795Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 38
[INFO]  2018-02-01T18:49:50.317Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 39
[INFO]  2018-02-01T18:49:50.739Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 40
[INFO]  2018-02-01T18:49:51.257Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 41
[INFO]  2018-02-01T18:49:51.257Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 42
[INFO]  2018-02-01T18:49:51.257Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Reading [/tmp/ukpga_20100013_en.pdf], page: 43
[INFO]  2018-02-01T18:49:51.258Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Cleaning text: Currently 91925 characters
[INFO]  2018-02-01T18:49:51.357Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Separating text: Currently 90650 characters
FutureWarning: split() requires a non-empty pattern match. [task_wordcount.py:88]
[INFO]  2018-02-01T18:49:51.575Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Saving descriptor for [/tmp/ukpga_20100013_en.pdf] as [/tmp/c2c142b0cf482def806a7d10c0f12001022b7a6266ca0658df367130c993d5d5-descriptor.json]
[INFO]  2018-02-01T18:49:51.997Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Saving [/tmp/c2c142b0cf482def806a7d10c0f12001022b7a6266ca0658df367130c993d5d5-wordcount.json]
[INFO]  2018-02-01T18:49:52.97Z a3ebad7b-0780-11e8-9747-d58c273a1af5  Resetting dropped connection: s3.eu-central-1.amazonaws.com
[INFO]  2018-02-01T18:49:52.276Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Created s3://serverless-wordcount-result/ukpga_20100013_en.pdf
[INFO]  2018-02-01T18:49:52.484Z  a3ebad7b-0780-11e8-9747-d58c273a1af5  Created s3://serverless-wordcount-archive/ukpga_20100013_en.pdf
END RequestId: a3ebad7b-0780-11e8-9747-d58c273a1af5
REPORT RequestId: a3ebad7b-0780-11e8-9747-d58c273a1af5  Duration: 19675.12 ms Billed Duration: 19700 ms Memory Size: 128 MB Max Memory Used: 39 MB  
```

(included as test.sh)

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