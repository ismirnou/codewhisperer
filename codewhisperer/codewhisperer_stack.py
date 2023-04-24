from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_sqs as sqs,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_sns as sns
)
from constructs import Construct

class CodewhispererStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #Create s3 bucket with name codewhisperer-examples with versioning enabled, auto delete objects and removal policy destroy
        bucket = s3.Bucket(self, "codewhisperer-examples",
                           versioned=True,
                           removal_policy=RemovalPolicy.DESTROY,
                           auto_delete_objects=True)
        
        # Create sqs queue with name codewhisperer-new-example with visibility timeout of 300 seconds, wait time of 20 seconds and removal policy destroy
        sqs_queue = sqs.Queue(self, "codewhisperer-new-example",
                              visibility_timeout=Duration.seconds(300),
                              receive_message_wait_time=Duration.seconds(20),
                              removal_policy=RemovalPolicy.DESTROY)
        
        # Create sns topic with name codewhisperer-new-example-topic
        sns_topic = sns.Topic(self, "codewhisperer-new-example-topic")
        
        # Create api gateway resource with name codewhisperer with path /get-examples and method GET backed by lambda function get_examples, code from s3 bucket codewhisperer-examples with key lambda/get_examples.zip, runtime python 3.8, handler get_examples.lambda_handler, proxy false, rest api name codewhisperer, description codewhisperer API, deploy options stage name dev
        apigateway = apigw.LambdaRestApi(self, "codewhisperer",
                                         handler=_lambda.Function(self, "get_examples",
                                                                   function_name="get_examples",
                                                                   code=_lambda.Code.from_bucket(bucket, key="lambda/get_examples.zip"),
                                                                   runtime=_lambda.Runtime.PYTHON_3_8,
                                                                   handler="get_examples.lambda_handler",
                                                                   environment={"S3_BUCKET": bucket.bucket_name},
                                                                   tracing=_lambda.Tracing.ACTIVE),
                                                                   proxy=False,
                                                                   rest_api_name="codewhisperer",
                                                                   description="codewhisperer API",
                                                                   deploy_options=apigw.StageOptions(stage_name="dev"))
