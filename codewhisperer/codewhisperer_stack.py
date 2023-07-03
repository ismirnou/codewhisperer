from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigatewayv2_alpha as apigwv2,
    aws_apigatewayv2_integrations_alpha as apigwv2_integrations,
    aws_apigatewayv2_authorizers_alpha as apigwv2_authorizers,
    aws_iam as iam,
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
        
        # Create a lambda function role with s3 read and write permissions for codewhisperers-examples bucket. Use inline policy. Don't use managed policy
        role = iam.Role(self, "codewhisperer-lambda-role",
                        assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                        inline_policies={
                            "s3-policy": iam.PolicyDocument(
                                    statements=[
                                        iam.PolicyStatement(
                                            actions=["s3:*"],
                                            resources=[bucket.bucket_arn, bucket.bucket_arn + "/*"],
                                            effect=iam.Effect.ALLOW
                                            )
                                            ]
                                            )
                                            })


        # Create get-api lambda function with name codewhisperer-api-get-lambda with inline code read from functions/api-get.py file and use lambda_handler handler, timeout of 300 seconds and memory size of 128 MB and use codewhisperer-lambda-role as lambda function role
        api_get_lambda = _lambda.Function(self, "codewhisperer-api-get-lambda",
                                        runtime=_lambda.Runtime.PYTHON_3_8,
                                        handler="api-get.lambda_handler",
                                        code=_lambda.Code.from_asset("functions"),
                                        timeout=Duration.seconds(300),
                                        memory_size=128,
                                        role=role)
        
        # Create put-api lambda function with name codewhisperer-api-put-lambda with inline code read from functions/api-put.py file and use lambda_handler handler, timeout of 300 seconds and memory size of 128 MB and use codewhisperer-lambda-role as lambda function role
        api_put_lambda = _lambda.Function(self, "codewhisperer-api-put-lambda",
                                        runtime=_lambda.Runtime.PYTHON_3_8,
                                        handler="api-put.lambda_handler",
                                        code=_lambda.Code.from_asset("functions"),
                                        timeout=Duration.seconds(300),
                                        memory_size=128,
                                        role=role)

                                                  
        # Create authorizer lambda function with name codewhisperer-authorizer-lambda with inline code read from functions/authorizer.py file and use lambda_handler handler. Use codewhisperer-lambda-role as lambda function role
        authorizer_lambda = _lambda.Function(self, "codewhisperer-authorizer-lambda",
                                        runtime=_lambda.Runtime.PYTHON_3_8,
                                        handler="authorizer.lambda_handler",
                                        code=_lambda.Code.from_asset("functions"),
                                        role=role)
        
        authorizer = apigwv2_authorizers.HttpLambdaAuthorizer("BooksAuthorizer", authorizer_lambda)


        # Create api gateway with name codewhisperer-api-gateway and use codewhisperer-api-get-lambda as api get lambda function, codewhisperer-api-put-lambda as api put lambda function and use authorizer lambda function as authorizer
        api_gateway = apigwv2.HttpApi(self, "codewhisperer-api-gateway",
                                      api_name="codewhisperer-api-gateway",
                                      create_default_stage=True,
                                      default_authorizer=authorizer)
        


        # Add get method to api gateway with name GET and use codewhisperer-api-get-lambda as integration api_gateway_v2_integrations HttpLambdaIntegration providing id: string, function: Function. Add authorizer.
        api_gateway.add_routes(
            path="/get",
            methods=[apigwv2.HttpMethod.GET],
            integration=apigwv2_integrations.HttpLambdaIntegration('get', api_get_lambda),
            authorizer=authorizer
            )

        # Add put method to api gateway with name PUT and use codewhisperer-api-put-lambda as integration. Use codewhisperer-authorizer-lambda as authorizer
        api_gateway.add_routes(
            path="/put",
            methods=[apigwv2.HttpMethod.PUT],
            integration=apigwv2_integrations.HttpLambdaIntegration('put', api_put_lambda),
            authorizer=authorizer
            )
