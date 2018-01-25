# Serverless Word Count #

- [x] Given an archive of multiple files to process
- [x] When the archive is placed in a bucket
- [ ] Then the files in the archive are examined
- [ ] and the words in the sentence fragments are counted in a dataframe
- [ ] and the data frame is exported to a configured target folder
- [x] and the processed archive is moved to a configured bucket.

Running
=======

Install AWS CLI
---------------

See Amazon docs: https://docs.aws.amazon.com/cli/latest/userguide/installing.html

Also for macos another option is Brew
```bash
$ brew install awscli
Warning: awscli 1.14.30 is already installed
$
```

When installed AWS CLI will report version information:
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

Configure the command linme environment with your AWS credentials:
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

(included as deploy.sh)

Test
----

Given an archive of multiple files to process
When the archive is placed in a bucket
```bash
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
TODO
$
```

and the processed archive is moved to a configured bucket
```bash
$ aws s3 ls "s3://serverless-wordcount-hopper/"
TODO     
$ aws s3 ls "s3://serverless-wordcount-archive/"
2018-01-25 01:53:18     219613 fragments-to-process-1K.tar.gz
$
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