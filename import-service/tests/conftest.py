import os
import pytest
from moto import mock_s3
import boto3

def pytest_configure(config):
    """Set up environment variables before any imports happen"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['BUCKET_NAME'] = 'test-bucket'

@pytest.fixture
def s3_client():
    """Create mocked S3 client."""
    with mock_s3():
        s3 = boto3.client('s3', region_name='us-east-1')
        bucket_name = os.environ['BUCKET_NAME']
        s3.create_bucket(Bucket=bucket_name)
        yield s3

@pytest.fixture
def valid_csv_content():
    """Provide test CSV content"""
    return (
        "title,description,price,count\n"
        "First Test Product,Test Description,10.99,5\n"
        "Second Test Product,Another Description,20.00,10"
    )