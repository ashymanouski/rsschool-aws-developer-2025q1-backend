import json
import pytest
import boto3
import os
from src.product_by_id import handler  # Remove PRODUCTS from import

def test_get_existing_product(dynamodb_client, lambda_context):

    dynamodb = boto3.resource('dynamodb')
    products_table = dynamodb.Table(os.environ['TABLE_NAME_PRODUCTS'])
    stocks_table = dynamodb.Table(os.environ['TABLE_NAME_STOCKS'])
    
    test_product = {
        'id': '1',
        'title': 'Test Product',
        'description': 'Test Description',
        'price': 100
    }
    
    test_stock = {
        'product_id': '1',
        'count': 5
    }
    
    products_table.put_item(Item=test_product)
    stocks_table.put_item(Item=test_stock)
    
    event = {
        'pathParameters': {
            'productId': '1'
        }
    }
    
    response = handler(event, lambda_context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['id'] == '1'
    assert body['title'] == 'Test Product'
    assert body['description'] == 'Test Description'
    assert body['price'] == 100
    assert body['count'] == 5

def test_product_not_found(dynamodb_client, lambda_context):
    event = {
        'pathParameters': {
            'productId': 'non-existent'
        }
    }
    
    response = handler(event, lambda_context)
    
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert body['message'] == 'Product not found'

def test_invalid_request(dynamodb_client, lambda_context):
    event = {}
    
    response = handler(event, lambda_context)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert 'message' in body