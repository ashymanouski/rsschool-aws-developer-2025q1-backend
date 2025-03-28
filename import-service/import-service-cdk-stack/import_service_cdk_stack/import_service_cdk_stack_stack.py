from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_iam as iam,
    aws_sqs as sqs,
    Duration,
    Tags,
    Fn
)
from constructs import Construct
from .settings import SETTINGS

class ImportServiceCdkStackStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.template_options.description = "Task #7: AWS Lambda Authorizer"

        tags = {
            "task": "7",
            "owner": "ashymanouski"
        }

        def apply_tags(resource):
            for key, value in tags.items():
                Tags.of(resource).add(key, value)

        authorizer_lambda_arn = Fn.import_value("AuthorizerLambdaArn")

        authorizer_invoke_role = iam.Role(
            self, 
            "AuthorizerInvokeRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            inline_policies={
                "InvokeLambdaAuthorizer": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["lambda:InvokeFunction"],
                            resources=[authorizer_lambda_arn],
                            effect=iam.Effect.ALLOW
                        )
                    ]
                )
            }
        )
        
        authorizer = apigw.TokenAuthorizer(
            self, 
            "ImportApiAuthorizer",
            handler=_lambda.Function.from_function_arn(
                self, 
                "AuthorizerFunction",
                authorizer_lambda_arn
            ),
            results_cache_ttl=Duration.seconds(0),
            assume_role=authorizer_invoke_role
        )

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
                allow_methods=["GET", "OPTIONS"],
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
            },
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.CUSTOM
        )


        smart_open_layer = _lambda.LayerVersion(
            self, 'SmartOpenLayer',
            code=_lambda.Code.from_asset('../layers/smart_open'),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description='Smart Open Layer for CSV streaming'
        )

        catalog_items_queue = sqs.Queue.from_queue_arn(
            self, "ImportToCatalogQueue",
            f"arn:aws:sqs:{self.region}:{self.account}:catalogItemsQueue"
        )

        import_file_parser = _lambda.Function(
            self, "ImportFileParser",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="import_file_parser.handler",
            code=_lambda.Code.from_asset("../src"),
            timeout=Duration.seconds(30),
            layers=[smart_open_layer],
            environment={
                "SQS_QUEUE_URL": catalog_items_queue.queue_url
            }
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

        import_file_parser.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'sqs:SendMessage'
                ],
                resources=[
                    catalog_items_queue.queue_arn
                ]
            )
        )

        import_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(import_file_parser),
            s3.NotificationKeyFilter(prefix="uploaded/")
        )

