from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigatewayv2_alpha as apigwv2,
    aws_iam as iam,
    aws_ssm as ssm,
)
from constructs import Construct

from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpLambdaAuthorizer, HttpLambdaResponseType
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
from aws_cdk import CfnOutput, CfnParameter


class CodewhispererStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # create cfn stack parameter with name prefix
        prefix = CfnParameter(self, "prefix",
                              type="String",
                              description="Prefix for all resources",
                              default="codewhisperer"
                              )

        # create cfn stack parameter with name apikey
        api_key = CfnParameter(self, "apikey",
                               type="String",
                               description="API key for the Codewhisperer API"
                               )

        # Create s3 bucket with name {prefix value}-cats with versioning enabled and removal policy destroy. Physical ID should be s3-cats. Block public access
        bucket = s3.Bucket(self, f"s3-cats",
                           bucket_name=f"{prefix.value_as_string}-cats",
                           versioned=True,
                           removal_policy=RemovalPolicy.DESTROY,
                           block_public_access=s3.BlockPublicAccess.BLOCK_ALL)

        # Create a lambda function role with s3 read and write permissions for created bucket. Use inline policy. Don't use managed policy. Use {prefix value}-lambda-role for role name
        role = iam.Role(self, "lambda-role",
                        role_name=f"{prefix.value_as_string}-lambda-role",
                        assumed_by=iam.ServicePrincipal(
                            "lambda.amazonaws.com"),
                        inline_policies={
                            "s3-policy": iam.PolicyDocument(
                                statements=[
                                    iam.PolicyStatement(
                                        actions=["s3:*"],
                                        resources=[
                                            bucket.bucket_arn, bucket.bucket_arn + "/*"],
                                        effect=iam.Effect.ALLOW
                                    )
                                ]
                            )
                        })

        # add permissions for lambda to send logs
        role.add_to_policy(iam.PolicyStatement(
            actions=["logs:*"],
            resources=["*"]
        ))

        # add permissions to get value from /auth/token ssm parameter
        role.add_to_policy(iam.PolicyStatement(
            actions=["ssm:GetParameter"],
            resources=["arn:aws:ssm:eu-west-1:*:parameter/auth/token"]
        ))

        # Create get-api lambda function with name {prefix value}-get-api with inline code read from functions/get-api.py file and use lambda_handler handler, timeout of 300 seconds and memory size of 128 MB and use {prefix value}-lambda-role as lambda function role
        api_get_lambda = _lambda.Function(self, "get-api-lambda",
                                          function_name=f"{prefix.value_as_string}-get-api",
                                          runtime=_lambda.Runtime.PYTHON_3_8,
                                          handler="get-api.lambda_handler",
                                          code=_lambda.Code.from_asset(
                                              "functions"),
                                          timeout=Duration.seconds(300),
                                          memory_size=128,
                                          role=role)

        # add enviroment variables to get-api lambda function BUCKET_NAME
        api_get_lambda.add_environment("BUCKET_NAME", bucket.bucket_name)

        # Create put-api lambda function with name {prefix value}-put-api with inline code read from functions/put-api.py file and use lambda_handler handler, timeout of 300 seconds and memory size of 128 MB and use {prefix value}-lambda-role as lambda function role
        api_put_lambda = _lambda.Function(self, "put-api-lambda",
                                          function_name=f"{prefix.value_as_string}-put-api",
                                          runtime=_lambda.Runtime.PYTHON_3_8,
                                          handler="put-api.lambda_handler",
                                          code=_lambda.Code.from_asset(
                                              "functions"),
                                          timeout=Duration.seconds(300),
                                          memory_size=128,
                                          role=role)

        # add enviroment variables to put-api lambda function BUCKET_NAME
        api_put_lambda.add_environment("BUCKET_NAME", bucket.bucket_name)

        # Create authorizer lambda function with name {prefix value}-auth with inline code read from functions/auth.py file and use lambda_handler handler. Use {prefix value}-lambda-role as lambda function role
        authorizer_lambda = _lambda.Function(self, "auth-lambda",
                                             function_name=f"{prefix.value_as_string}-auth",
                                             runtime=_lambda.Runtime.PYTHON_3_8,
                                             handler="auth.lambda_handler",
                                             code=_lambda.Code.from_asset(
                                                 "functions"),
                                             role=role)

        # create ssm secure string parameter with name /auth/token and value from apikey parameter
        ssm.StringParameter(self, "token",
                            parameter_name="/auth/token",
                            string_value=api_key.value_as_string)

        # add enviroment variables to authorizer lambda function PARAMETER_STORE_NAME
        authorizer_lambda.add_environment(
            "PARAMETER_STORE_NAME", "/auth/token")

        # Create authorizer lambda-auth
        authorizer = HttpLambdaAuthorizer("lambda-auth", authorizer_lambda,
                                          identity_source=[], results_cache_ttl=Duration.seconds(0), response_types=[HttpLambdaResponseType.IAM]
                                          )

        # Create http v2 api gateway with name {prefix value}
        api_gateway = apigwv2.HttpApi(self, "api-gateway",
                                      api_name=f"{prefix.value_as_string}-cats",
                                      create_default_stage=True
                                      )

        # Add get method to api gateway with name /cats/{proxy+} and use self-service-api-get-lambda as integration api_gateway_v2_integrations HttpLambdaIntegration providing id: string, function: Function. Add authorizer.
        api_gateway.add_routes(
            path="/cats/{proxy+}",
            methods=[apigwv2.HttpMethod.GET],
            integration=HttpLambdaIntegration(
                'get', api_get_lambda, payload_format_version=apigwv2.PayloadFormatVersion.VERSION_1_0),
            authorizer=authorizer
        )

        # Add put method to api gateway with name /cats/{proxy+} and use self-service-api-put-lambda as integration. Use self-service-authorizer-lambda as authorizer
        api_gateway.add_routes(
            path="/cats/{proxy+}",
            methods=[apigwv2.HttpMethod.PUT],
            integration=HttpLambdaIntegration(
                'put', api_put_lambda, payload_format_version=apigwv2.PayloadFormatVersion.VERSION_1_0),
            authorizer=authorizer
        )

        # create stack output for api gateway url
        CfnOutput(self, "api-gateway-url",
                  value=api_gateway.api_endpoint,
                  description="api gateway url"
                  )
