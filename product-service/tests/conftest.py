import os
import json
import pytest
from moto import mock_dynamodb, mock_sns, mock_sqs
import boto3

class MockContext:
    def __init__(self):
        self.function_name = "test-function"
        self.function_version = "test-version"
        self.memory_limit_in_mb = 128
        self.aws_request_id = "test-request-id"
        self.log_group_name = "test-log-group"
        self.log_stream_name = "test-log-stream"

@pytest.fixture
def lambda_context():
    return MockContext()

def pytest_configure(config):
    """Set up environment variables before any imports happen"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['TABLE_NAME_PRODUCTS'] = 'products'
    os.environ['TABLE_NAME_STOCKS'] = 'stocks'
    os.environ['SNS_TOPIC_ARN'] = f"arn:aws:sns:{os.environ['AWS_DEFAULT_REGION']}:123456789012:test-topic"

@pytest.fixture
def dynamodb_client():
    """Create mocked DynamoDB client and tables."""
    with mock_dynamodb():
        client = boto3.client('dynamodb', region_name=os.environ['AWS_DEFAULT_REGION'])
        
        client.create_table(
            TableName=os.environ['TABLE_NAME_PRODUCTS'],
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
        )
        
        client.create_table(
            TableName=os.environ['TABLE_NAME_STOCKS'],
            KeySchema=[{'AttributeName': 'product_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'product_id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
        )
        
        yield client

@pytest.fixture
def sns_client():
    """Create mocked SNS client and topic."""
    with mock_sns():
        client = boto3.client('sns', region_name=os.environ['AWS_DEFAULT_REGION'])
        topic = client.create_topic(Name='test-topic')
        yield client

@pytest.fixture
def sqs_client():
    """Create mocked SQS client."""
    with mock_sqs():
        client = boto3.client('sqs', region_name=os.environ['AWS_DEFAULT_REGION'])
        yield client

@pytest.fixture
def test_event():
    """Provide test event data"""
    return {
        'Records': [{
            'body': json.dumps({
                'id': '1',
                'title': 'Test Product',
                'description': 'Test Description',
                'price': 100,
                'count': 5
            })
        }]
    }

@pytest.fixture
def invalid_test_event():
    """Provide invalid test event data"""
    return {
        'Records': [{
            'body': json.dumps({
                'id': '1'
            })
        }]
    }