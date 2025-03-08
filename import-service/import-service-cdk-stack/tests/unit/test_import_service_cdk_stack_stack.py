import aws_cdk as core
import aws_cdk.assertions as assertions

from import_service_cdk_stack.import_service_cdk_stack_stack import ImportServiceCdkStackStack

# example tests. To run these tests, uncomment this file along with the example
# resource in import_service_cdk_stack/import_service_cdk_stack_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ImportServiceCdkStackStack(app, "import-service-cdk-stack")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
