# Serverless Word Count #

- [x] Given an archive of multiple files to process
- [x] When the archive is placed in a bucket
- [x] Then the files in the archive are examined
- [x] and the words in the sentence fragments are counted
- [x] and the results are exported to a configured target folder
- [ ] and the processed archive is moved to a configured bucket.

The archive format is a .tar.gz of files with no folder structure:
```bash
$ tar tzf fragments-to-process-1K.tar.gz | head -5
00018db223b66a677b6e146567c7e7bba8d1c59e207555997d17238dbe6f50cc.json
00028bc8a2fd8db9264467261c75842b7dfb37f7080fda95041128a8de11d7d6.json
00035fc8688e35dd3080eeaa2e13bf7a2471f611fbe1f804cbc11d01b966e6f5.json
0003db3073bd9f19f2b26cc6e802c2f9574085a030d487041a08214572d8842d.json
000490f3414c3d0234aaaf6caae452c08fbd21d6903c5b1dfd8c26cba08afdef.json
$ 
```

The files themselves are JSON containing metadata and a document fragment:
```json
{
   "countryOfOrigin": "GB",
   "downloadedFileAt": "2017-06-25T00:16:00.304541",
   "downloadedFilename": "4d52dafd817564fcb4f226472d8897637c4b8ec389a9cb7294959370443011b3.pdf",
   "fragment": "(7)A statutory instrument contai\nning an order under subsection (4) is subject to\nannulment in pursuance of a resolution of the House of Commons.",
   "geographical_extent": "ukpga",
   "labels": "legislation, non-fiction",
   "language": "en",
   "source": "legislation.gov.uk",
   "timestamp": "2017-06-25T00:01:07Z+0100",
   "type": "text_descriptor",
   "url": "http://www.legislation.gov.uk/ukpga/2010/13/pdfs/ukpga_20100013_en.pdf",
   "year": "2010"
}
```

The output is a wordcount over all the fragments:
```json
{
   "a": 164,
   "abandonment": 1,
   "abbey": 1,
   "aberuthven": 1,
   "about": 11,
   "abstract": 1,
   "ac": 1,
   "academies": 1,
   "accordance": 1,
   "accordingly": 2,
...
   "works": 4,
   "would": 3,
   "y": 2,
   "year": 2,
   "years": 3,
   "young": 4,
   "z": 1,
   "za": 1
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

Configure AWS
-------------

Create a IAM user with the following Polices:
* Amazon: AWSLambdaFullAccess
* Amazon: AmazonS3FullAccess
* Amazon: IAMFullAccess
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
$ mkdir -p "./target/dist"
$ cp "./lambda_wordcount.py" "./target/dist/."
$ cp "./task_wordcount.py" "./target/dist/."
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
$ rm -rf "./target/dist"
$
```

(included as deploy.sh)

Test
----

Given an archive of multiple files to process
When the archive is placed in a bucket
```bash
$ aws s3 rm "s3://serverless-wordcount-hopper/" --recursive
$ aws s3 rm "s3://serverless-wordcount-result/" --recursive
$ aws s3 rm "s3://serverless-wordcount-archive/" --recursive
$ aws s3 cp "fragments-to-process-1K.tar.gz" "s3://serverless-wordcount-hopper/"
upload: ./fragments-to-process-1K.tar.gz to s3://serverless-wordcount-hopper/fragments-to-process-1K.tar.gz
$
```

When the archive is placed in a bucket
```bash
$ aws s3 ls "s3://serverless-wordcount-hopper/"
2018-01-24 18:53:17     219613 fragments-to-process-1K.tar.gz   
$
```

Then the files in the archive are examined
and the words in the sentence fragments are counted in a dataframe
and the data frame is exported to a configured target folder
```bash
$ aws s3 ls "s3://serverless-wordcount-result/"
2018-01-25 23:23:11      61611 fragments-to-process-1K.tar.gz-result.json
$
```

and the processed archive is moved to a configured bucket
```bash
$ aws s3 ls "s3://serverless-wordcount-hopper/" --summarize
TODO     
$ aws s3 ls "s3://serverless-wordcount-archive/"
2018-01-25 01:53:18     219613 fragments-to-process-1K.tar.gz
$
```

Observe
-------

The CloudWatch console shows serveral log events throughout the several seconds of execution:
```
[INFO]  2018-01-25T22:23:04.792Z  Found credentials in environment variables.
START RequestId: 4fb498c2-021e-11e8-a1c0-6b0f475e0486 Version: $LATEST
[INFO]  2018-01-25T22:23:04.829Z  4fb498c2-021e-11e8-a1c0-6b0f475e0486  Processing all records...
[INFO]  2018-01-25T22:23:04.850Z  4fb498c2-021e-11e8-a1c0-6b0f475e0486  Starting new HTTPS connection (1): s3.eu-central-1.amazonaws.com
[INFO]  2018-01-25T22:23:07.432Z  4fb498c2-021e-11e8-a1c0-6b0f475e0486  Scanning for fragments in: [/tmp/fragments]
[INFO]  2018-01-25T22:23:09.830Z  4fb498c2-021e-11e8-a1c0-6b0f475e0486  Saving [/tmp/bb1d3614-a685-4370-974d-0e02186d20e0]
[INFO]  2018-01-25T22:23:10.88Z 4fb498c2-021e-11e8-a1c0-6b0f475e0486  Created s3://serverless-wordcount-result/fragments-to-process-1K.tar.gz
[INFO]  2018-01-25T22:23:10.159Z  4fb498c2-021e-11e8-a1c0-6b0f475e0486  Created s3://serverless-wordcount-archive/fragments-to-process-1K.tar.gz
END RequestId: 4fb498c2-021e-11e8-a1c0-6b0f475e0486
REPORT RequestId: 4fb498c2-021e-11e8-a1c0-6b0f475e0486  Duration: 5330.27 ms  Billed Duration: 5400 ms Memory Size: 128 MB  Max Memory Used: 41 MB  
```

(included as test.sh)

Cloud Formation Custom Policy
=============================

This custom policy for Cloud Formation and IAM actions was generated with the Visual Editor:
```json
{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Sid":"VisualEditor0",
         "Effect":"Allow",
         "Action":[
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
         "Resource":[
            "arn:aws:cloudformation:*:*:stack/*/*",
            "arn:aws:cloudformation:*:*:transform/Serverless-2016-10-31"
         ]
      },
      {
          "Sid":"VisualEditor1",
          "Effect":"Allow",
          "Action":[
               "iam:CreateRole",
               "iam:DeleteRole",
               "iam:DetachRolePolicy",
               "iam:AttachRolePolicy"
          ],
          "Resource":"*"
      }
   ]
}
```