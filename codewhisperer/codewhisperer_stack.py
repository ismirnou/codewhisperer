from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_sqs as sqs,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_sns as sns,
    aws_apigateway as apigw
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

        # Create api lambda function with name codewhisperer-api-lambda with inline code read from functions/api.py file and use lambda_handler handler, timeout of 300 seconds and memory size of 128 MB
        api_lambda = _lambda.Function(self, "codewhisperer-api-lambda",
                                        runtime=_lambda.Runtime.PYTHON_3_8,
                                        handler="api.lambda_handler",
                                        code=_lambda.Code.from_asset("functions"),
                                        timeout=Duration.seconds(300),
                                        memory_size=128)
                                                  
        # Create authorizer lambda function with name codewhisperer-authorizer-lambda with inline code read from functions/authorizer.py file and use lambda_handler handler
        authorizer_lambda = _lambda.Function(self, "codewhisperer-authorizer-lambda",
                                        runtime=_lambda.Runtime.PYTHON_3_8,
                                        handler="authorizer.lambda_handler",
                                        code=_lambda.Code.from_asset("functions"))
        
         # Create notificator lambda function with name codewhisperer-notificator-lambda with inline code read from functions/notificator.py file and use lambda_handler handler
        notificator_lambda = _lambda.Function(self, "codewhisperer-notificator-lambda",
                                        runtime=_lambda.Runtime.PYTHON_3_8,
                                        handler="notificator.lambda_handler",
                                        code=_lambda.Code.from_asset("functions"))
        
        # Create Lambda rest api with name codewhisperer-api-gateway
        api_gateway = apigw.LambdaRestApi(self, "codewhisperer-api-gateway",
                                          handler=api_lambda,
                                          proxy=False,
                                          deploy_options={
                                                'logging_level': apigw.MethodLoggingLevel.INFO,
                                                'data_trace_enabled': True,
                                                'metrics_enabled': True,
                                                'tracing_enabled': True
                                                })
        
        # Create get-examples resource to api_gateway root
        examples_resource = api_gateway.root.add_resource("get-examples")

        # Add GET method examples resource with get-examples route and api_lambda
        examples_resource.add_method("GET", api_lambda)

        # Create put-example resource to api_gateway root with authorizer_lambda as authorizer
        put_example_resource = api_gateway.root.add_resource("put-example")
        put_example_resource.add_method("PUT", api_lambda, authorizer=apigw.LambdaAuthorizer(self, "authorizer", handler=authorizer_lambda))
