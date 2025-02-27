from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    Tags
)
from constructs import Construct

class ProductServiceCdkStackStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.template_options.description = "Task #4: Integration with DynamoDB"

        tags = {
            "task": "4",
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
