from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
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

        import_bucket = s3.Bucket.from_bucket_name(
            self, 'ImportBucket',
            bucket_name=SETTINGS["IMPORT_BUCKET_NAME"]
        )

        import_products_file = _lambda.Function(
            self, "ImportProductsFile",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="import_products_file.handler",
            code=_lambda.Code.from_asset("../src"),
            timeout=Duration.seconds(30),
            environment={
                "BUCKET_NAME": import_bucket.bucket_name
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
                    f'arn:aws:s3:::{import_bucket.bucket_name}'
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
                    f'arn:aws:s3:::{import_bucket.bucket_name}/*'
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


        smart_open_layer = _lambda.LayerVersion(
            self, 'SmartOpenLayer',
            code=_lambda.Code.from_asset('../layers/smart_open'),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description='Smart Open Layer for CSV streaming'
        )

        import_file_parser = _lambda.Function(
            self, "ImportFileParser",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="import_file_parser.handler",
            code=_lambda.Code.from_asset("../src"),
            timeout=Duration.seconds(30),
            layers=[smart_open_layer]
        )
        apply_tags(import_file_parser)

        import_file_parser.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    's3:GetObject',
                    's3:GetObjectAttributes',
                    's3:DeleteObject'
                ],
                resources=[
                    f'arn:aws:s3:::{import_bucket.bucket_name}/uploaded/*'
                ]
            )
        )

        import_file_parser.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    's3:PutObject'
                ],
                resources=[
                    f'arn:aws:s3:::{import_bucket.bucket_name}/parsed/*'
                ]
            )
        )

        import_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(import_file_parser),
            s3.NotificationKeyFilter(prefix="uploaded/")
        )

