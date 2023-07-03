# create a function to get jpeg image from api gw post request and save to s3 bucket. Use BUCKET_NAME environment variable. Use path as an object key. Put "new image is uploaded" to the api gw responce.

import boto3
import os

# convert base64 string to binary string

import base64


def base64_to_binary(base64_string):
    return base64.b64decode(base64_string)


# Create constant for BUCKET_NAME. Get it from env variable.
BUCKET_NAME = os.environ['BUCKET_NAME']


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = BUCKET_NAME
    # remove first / from path
    event['path'] = event['path'][1:]
    # convert body to base64 binary string
    event['body'] = event['body'].encode('utf-8')
    # convert base64 body to binary string
    event['body'] = base64_to_binary(event['body'])
    s3.put_object(Bucket=bucket_name, Key=event['path'], Body=event['body'])
    # return response with "new {key} is uploaded message". Put key name

    return {
        'statusCode': 200,
        'body': f"new {event['path']} is uploaded"
    }
