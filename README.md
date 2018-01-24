# Serverless lambda example #

Given a bucket with a create trigger
and a destination bucket is named in the environment 
When an object is created
Then the object is copied to the destination bucket

Running
=======

Install AWS CLI
---------------

See Amazon docs: https://docs.aws.amazon.com/cli/latest/userguide/installing.html

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
* Custom: Cloud Formation Custom Policy (below).

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

Create an S3 deployment bucket:
```bash
aws s3 mb s3://serverless-deploy-13667
```

Package AWS Lambda with Serverless template:
```bash
$ aws cloudformation package \
>   --template-file "serverless.yaml" \
>   --output-template-file "serverless_output.yaml" \
>   --s3-bucket "serverless-deploy-13667"

Uploading to 480a940f6f8347ef3cf31bba3c361c99  17613 / 17613.0  (100.00%)
Successfully packaged artifacts and wrote output template to file serverless_output.yaml.
Execute the following command to deploy the packaged template
aws cloudformation deploy --template-file /Users/antony/projects/aws-serverless-lambda-python/serverless_output.yaml --stack-name <YOUR STACK NAME>
$ 
```

Deploy AWS Lambda with Serverless template:
```bash
$ aws cloudformation deploy \
>    --template-file "serverless_output.yaml" \
>    --stack-name "serverless-stack" \
>    --capabilities CAPABILITY_IAM

Waiting for changeset to be created..
Waiting for stack create/update to complete
Successfully created/updated stack - serverless-stack
$
```

(included as deploy.sh)

Test
----

Create a new file and store it in the source bucket.

```bash
$ echo "Serverless test file" > "test.txt"
$ aws s3 cp "test.txt" "s3://serverless-source-bucket/test.txt"
```

Observe that the new file has been copied to the destination bucket.

```bash
$ aws s3 ls "s3://serverless-destination-bucket/"
```

(included as test.sh)

Cloud Formation Custom Policy
=============================

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