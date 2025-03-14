import os
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_lambda_event_sources as lambda_events,
    Duration,
    Tags
)
from constructs import Construct

class ProductServiceCdkStackStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.template_options.description = "Task #6: AWS SQS & SNS"

        tags = {
            "task": "6",
            "owner": "ashymanouski"
        }

        def apply_tags(resource):
            for key, value in tags.items():
                Tags.of(resource).add(key, value)

        get_products_list = _lambda.Function(
            self, 'GetProductsList',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='products_list.handler',
            code=_lambda.Code.from_asset('../src'),
            environment={
                'TABLE_NAME_PRODUCTS': 'products',
                'TABLE_NAME_STOCKS': 'stocks'
            }            
        )
        apply_tags(get_products_list)

        get_products_list.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'dynamodb:Scan'
                ],
                resources=[
                    f'arn:aws:dynamodb:{self.region}:{self.account}:table/products',
                    f'arn:aws:dynamodb:{self.region}:{self.account}:table/stocks'
                ]
            )
        )

        get_product_by_id = _lambda.Function(
            self, 'GetProductById',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='product_by_id.handler',
            code=_lambda.Code.from_asset('../src'),
            environment={
                'TABLE_NAME_PRODUCTS': 'products',
                'TABLE_NAME_STOCKS': 'stocks'
            } 
        )
        apply_tags(get_product_by_id)

        get_product_by_id.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'dynamodb:GetItem'
                ],
                resources=[
                    f'arn:aws:dynamodb:{self.region}:{self.account}:table/products',
                    f'arn:aws:dynamodb:{self.region}:{self.account}:table/stocks'
                ]
            )
        )

        create_product = _lambda.Function(
            self, 'CreateProduct',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='create_product.handler',
            code=_lambda.Code.from_asset('../src'),
            environment={
                'TABLE_NAME_PRODUCTS': 'products',
                'TABLE_NAME_STOCKS': 'stocks'
            }
        )
        apply_tags(create_product)

        create_product.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'dynamodb:PutItem'
                ],
                resources=[
                    f'arn:aws:dynamodb:{self.region}:{self.account}:table/products',
                    f'arn:aws:dynamodb:{self.region}:{self.account}:table/stocks'
                ]
            )
        )

        catalog_items_queue = sqs.Queue(
            self, "CatalogItemsQueue",
            queue_name="catalogItemsQueue",
            visibility_timeout=Duration.seconds(10)
        )
        apply_tags(catalog_items_queue)

        create_product_topic = sns.Topic(
            self, "CreateProductTopic",
            topic_name="createProductTopic"
        )
        apply_tags(create_product_topic)

        # Subscription for all products
        notification_emails = os.getenv('NOTIFICATION_EMAILS', '').split(',')
        for email in notification_emails:
            if email:
                create_product_topic.add_subscription(
                    subscriptions.EmailSubscription(email)
                )

        # Subscription for expensive products
        notification_emails_expensive = os.getenv('NOTIFICATION_EMAILS_EXPENSIVE', '').split(',')
        for email in notification_emails_expensive:
            if email:
                create_product_topic.add_subscription(
                    subscriptions.EmailSubscription(email,
                        filter_policy={
                            "price": sns.SubscriptionFilter.numeric_filter(
                                greater_than_or_equal_to=50
                            )
                        }
                    )
                )

        # Subscription for cheap products
        notification_emails_cheap = os.getenv('NOTIFICATION_EMAILS_CHEAP', '').split(',')
        for email in notification_emails_cheap:
            if email:
                create_product_topic.add_subscription(
                    subscriptions.EmailSubscription(email,
                        filter_policy={
                            "price": sns.SubscriptionFilter.numeric_filter(
                                less_than=50
                            )
                        }
                    )
                )

        catalog_batch_process = _lambda.Function(
            self, 'CatalogBatchProcess',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='catalog_batch_process.handler',
            code=_lambda.Code.from_asset('../src'),
            environment={
                'TABLE_NAME_PRODUCTS': 'products',
                'TABLE_NAME_STOCKS': 'stocks',
                'SNS_TOPIC_ARN': create_product_topic.topic_arn
            },
            timeout=Duration.seconds(10)
        )
        apply_tags(catalog_batch_process)

        catalog_batch_process.add_event_source(
            lambda_events.SqsEventSource(
                catalog_items_queue,
                batch_size=5,
                max_batching_window=Duration.seconds(10),
                max_concurrency=2
            )
        )

        catalog_batch_process.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'dynamodb:PutItem'
                ],
                resources=[
                    f'arn:aws:dynamodb:{self.region}:{self.account}:table/products',
                    f'arn:aws:dynamodb:{self.region}:{self.account}:table/stocks'
                ]
            )
        )

        catalog_batch_process.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'sns:Publish'
                ],
                resources=[
                    create_product_topic.topic_arn
                ]
            )
        )

        apigateway = apigw.RestApi(
            self, 'ProductServiceAPI',
            rest_api_name='ProductService',
            description="Product Service API Gateway",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=['GET', 'OPTIONS']
            )
        )
        apply_tags(apigateway)

        products = apigateway.root.add_resource('products')
        products.add_method('GET', apigw.LambdaIntegration(get_products_list))
        products.add_method('POST', apigw.LambdaIntegration(create_product))

        product_by_id = products.add_resource('{productId}')
        product_by_id.add_method('GET', apigw.LambdaIntegration(get_product_by_id))
