import aws_cdk as core
import aws_cdk.assertions as assertions

from authorization_service_cdk_stack.authorization_service_cdk_stack_stack import AuthorizationServiceCdkStackStack

# example tests. To run these tests, uncomment this file along with the example
# resource in authorization_service_cdk_stack/authorization_service_cdk_stack_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AuthorizationServiceCdkStackStack(app, "authorization-service-cdk-stack")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
