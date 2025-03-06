from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    Duration,
    Tags
)
from constructs import Construct
from .settings import SETTINGS

class ImportServiceCdkStackStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.template_options.description = "Task #5: Integration with S3"

        tags = {
            "task": "5",
            "owner": "ashymanouski"
        }

        def apply_tags(resource):
            for key, value in tags.items():
                Tags.of(resource).add(key, value)

        # import_bucket = s3.Bucket(
        #     self, "ImportBucket",
        #     cors=[s3.CorsRule(
        #         allowed_methods=[s3.HttpMethods.PUT],
        #         allowed_origins=["*"],
        #         allowed_headers=["*"]
        #     )]
        # )
        # apply_tags(import_bucket)

        import_products_file = _lambda.Function(
            self, "ImportProductsFile",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="import_products_file.handler",
            code=_lambda.Code.from_asset("../src"),
            timeout=Duration.seconds(30),
            environment={
                "BUCKET_NAME": SETTINGS["IMPORT_BUCKET_NAME"]
            }
        )
        apply_tags(import_products_file)

        import_products_file.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    's3:ListBucket'
                ],
                resources=[
                    f'arn:aws:s3:::{SETTINGS["IMPORT_BUCKET_NAME"]}'
                ]
            )
        )

        import_products_file.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    's3:PutObject',
                    's3:GetObject',
                    's3:GetObjectAttributes'
                ],
                resources=[
                    f'arn:aws:s3:::{SETTINGS["IMPORT_BUCKET_NAME"]}/*'
                ]
            )
        )

        apigateway = apigw.RestApi(
            self, "ImportServiceApi",
            rest_api_name='ImportService',
            description="Import Service API Gateway",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=["*"],
                allow_methods=["GET"],
                allow_headers=["*"]
            )
        )
        apply_tags(apigateway)

        import_resource = apigateway.root.add_resource("import")
        import_resource.add_method(
            "GET",
            apigw.LambdaIntegration(import_products_file),
            request_parameters={
                "method.request.querystring.name": True
            }
        )

