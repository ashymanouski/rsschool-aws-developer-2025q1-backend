import aws_cdk as core
import aws_cdk.assertions as assertions

from product_service_cdk_stack.product_service_cdk_stack_stack import ProductServiceCdkStackStack

# example tests. To run these tests, uncomment this file along with the example
# resource in product_service_cdk_stack/product_service_cdk_stack_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ProductServiceCdkStackStack(app, "product-service-cdk-stack")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
