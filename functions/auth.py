# create function to get secure value from aws parameter store. Use PARAMETER_STORE_NAME as the name of the parameter store.
import json
import boto3
import os


def get_secure_value(parameter_store_name):
    ssm = boto3.client('ssm')
    parameter = ssm.get_parameter(
        Name=parameter_store_name, WithDecryption=True)
    return parameter['Parameter']['Value']

# Create constant for PARAMETER_STORE_NAME. Get it from env variable.x


PARAMETER_STORE_NAME = os.getenv('PARAMETER_STORE_NAME')


# create function "allow_request" to return api gateway lambda authorizer response. Use 1.0 format version.

def allow_request():
    print('allow')
    return {
        'principalId': "*",
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': 'Allow',
                    'Resource': '*'
                }
            ]
        }
    }

# create function "deny_request" to return api gateway lambda authorizer response. Use 1.0 format version


def deny_request():
    print('deny')
    return {
        'principalId': "*",
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': 'Deny',
                    'Resource': '*'
                }
            ]
        }
    }


# create custome API Gateway Lambda authorizer for GET requests. Get token from header api-key and check if it is equal to the value of the parameter store.

def lambda_handler(event, context):
    # validate if key "api-key" exists in headers. If not, return deny_request()
    if 'api-key' not in event['headers']:
        return deny_request()
    token = event['headers']['api-key']
    if token == get_secure_value(PARAMETER_STORE_NAME):
        return allow_request()
    else:
        return deny_request()


# create function "deny_request" to return api gateway lambda authorizer response. Use 2.0 format version
