# create function to get request path from api gw event
import base64
import boto3
import os

# add funcionality to get request path function: remove first '/' from the path


def remove_first_slash(path):
    return path[1:]


def get_request_path(event):
    return event['requestContext']['path']


def test_get_request_path():
    event = {'requestContext': {'path': '/test'}}
    assert (get_request_path(event) == '/test')

# create function to get .jpeg from s3 bucket by object key. Return output as api gw responce. Use BUCKET_NAME variable to set bucket name.


def get_jpeg_from_s3(object_key):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(BUCKET_NAME)
    obj = bucket.Object(object_key)
    return obj.get()['Body'].read()


def test_get_jpeg_from_s3():
    assert (get_jpeg_from_s3('test.jpeg') == b'')


# Create constant for BUCKET_NAME. Get it from env variable.
BUCKET_NAME = os.environ['BUCKET_NAME']

# create function for return api gw responce with content-type image/jpeg


def return_response(status_code, body):
    response = {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "image/jpeg"
        },
        "body": body,
        "isBase64Encoded": True
    }
    return response

# create function for encode body to base64


def encode_body(body):
    return base64.b64encode(body).decode()


# create function to get list of keys for objects in bucket by prefix. Exclude keys with / at the end of key. Return list as a string
def list_objects_in_bucket_by_prefix(prefix):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    objects = []
    for object in response['Contents']:
        if not object['Key'].endswith('/'):
            objects.append(object['Key'])
    # convert list objects to valid json string with "
    return str(objects).replace("'", '"')


# create api gateway responce object for application/json


def api_gw_responce(body, status_code):
    return {
        "statusCode": status_code,
        "body": body,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    }


# create lambda handler function


def lambda_handler(event, context):
    # get request path from event and remove first '/'
    request_path = remove_first_slash(get_request_path(event))
    # get list of objects in bucket by prefix if request_path finish with /
    if request_path.endswith('/'):
        objects = list_objects_in_bucket_by_prefix(request_path)
        # create api gateway responce object for application/json
        return api_gw_responce(objects, 200)
    # if request_path is not finish with / get jpeg from s3 bucket by object key. Return api gw response as a content type image/jpeg
    else:
        body = get_jpeg_from_s3(request_path)
        return return_response(200, encode_body(body))
