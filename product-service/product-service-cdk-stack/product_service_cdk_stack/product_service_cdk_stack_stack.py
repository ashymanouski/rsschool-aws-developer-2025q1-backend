from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    Tags
)
from constructs import Construct

class ProductServiceCdkStackStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.template_options.description = "Task #3: Product Service Stack with Lambda functions and API Gateway"

        tags = {
            "task": "3",
            "owner": "ashymanouski"
        }

        def apply_tags(resource):
            for key, value in tags.items():
                Tags.of(resource).add(key, value)

        get_products_list = _lambda.Function(
            self, 'GetProductsList',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='products_list.handler',
            code=_lambda.Code.from_asset('../src')
        )
        apply_tags(get_products_list)

        get_product_by_id = _lambda.Function(
            self, 'GetProductById',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='product_by_id.handler',
            code=_lambda.Code.from_asset('../src')
        )
        apply_tags(get_product_by_id)

        apigateway = apigw.RestApi(
            self, 'ProductServiceAPI',
            rest_api_name='ProductService',
            description="Product Service API Gateway",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
#                allow_methods=apigw.Cors.ALL_METHODS
                allow_methods=['GET', 'OPTIONS'] #https://github.com/aws-samples/aws-cdk-examples/blob/main/python/api-cors-lambda/app.py
            )
        )
        apply_tags(apigateway)


        products = apigateway.root.add_resource('products')
        products.add_method('GET', apigw.LambdaIntegration(get_products_list))

        product_by_id = products.add_resource('{productId}')
        product_by_id.add_method('GET', apigw.LambdaIntegration(get_product_by_id))
