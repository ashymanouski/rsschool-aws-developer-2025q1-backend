import json
import pytest
import os
import boto3
from src.catalog_batch_process import handler

def test_successful_processing(dynamodb_client, sns_client, test_event, lambda_context):

    dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_DEFAULT_REGION'])
    
    handler(test_event, lambda_context)
    
    products_table = dynamodb.Table(os.environ['TABLE_NAME_PRODUCTS'])
    product = products_table.get_item(Key={'id': '1'})['Item']
    
    assert product['title'] == 'Test Product'
    assert product['description'] == 'Test Description'
    assert product['price'] == 100
    
    stocks_table = dynamodb.Table(os.environ['TABLE_NAME_STOCKS'])
    stock = stocks_table.get_item(Key={'product_id': '1'})['Item']
    assert stock['count'] == 5

def test_sns_notification(dynamodb_client, sns_client, sqs_client, test_event, lambda_context):
    queue = sqs_client.create_queue(QueueName='test-queue')
    queue_url = queue['QueueUrl']
    
    queue_arn = sqs_client.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['QueueArn']
    )['Attributes']['QueueArn']
    
    sns_client.subscribe(
        TopicArn=os.environ['SNS_TOPIC_ARN'],
        Protocol='sqs',
        Endpoint=queue_arn
    )

    handler(test_event, lambda_context)
    
    messages = sqs_client.receive_message(QueueUrl=queue_url)
    assert 'Messages' in messages
    message_body = json.loads(messages['Messages'][0]['Body'])
    assert 'Test Product' in message_body['Message']

def test_invalid_product_data(dynamodb_client, sns_client, invalid_test_event, lambda_context):
    with pytest.raises(KeyError):
        handler(invalid_test_event, lambda_context)