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

Configure AWS
-------------

Create a IAM user with the following Amazon polices:
* AWSLambdaFullAccess
* AmazonS3FullAccess
* IAMFullAccess
* AWSCloudFormationReadOnlyAccess

And this Cloud Formation Custom Policy below.

Package and Deploy
------------------

Package AWS Lambda with Serverless template

```bash
aws cloudformation package
   --template-file "serverless.yaml" \
   --output-template-file "serverless_output.yaml" \
   --s3-bucket "serverless-deploy"
```

Deploy AWS Lambda with Serverless template

```bash
aws cloudformation deploy \
   --template-file "serverless_output.yaml" \
   --stack-name "serverless_stack" \
   --capabilities CAPABILITY_IAM
```

(included as deploy.sh)

Test
----

Create a new file and store it in the source bucket.

```bash
echo "Serverless test file" > "test.txt"
aws s3 cp "test.txt" "s3://serverless-source-bucket/test.txt"
```

Observe that the new file has been copied to the destination bucket.

```bash
aws s3 ls "s3://serverless-destination-bucket/"
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