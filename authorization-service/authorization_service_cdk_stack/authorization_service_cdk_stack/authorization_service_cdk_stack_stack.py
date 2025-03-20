# authorization_service_cdk_stack/authorization_service_cdk_stack_stack.py
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    CfnOutput
)
from constructs import Construct
from dotenv import dotenv_values

class AuthorizationServiceCdkStackStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.template_options.description = "Task #7: Authorization"

        credentials = dotenv_values(".env")

        basic_authorizer_lambda = _lambda.Function(
            self,
            "basicAuthorizer",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="basic_authorizer.handler",
            code=_lambda.Code.from_asset("../src"),
            environment=credentials,
            function_name="basicAuthorizer"
        )

        CfnOutput(
            self,
            "AuthorizerLambdaArn",
            value=basic_authorizer_lambda.function_arn,
            description="Basic Authorizer Lambda ARN",
            export_name="AuthorizerLambdaArn"
        )