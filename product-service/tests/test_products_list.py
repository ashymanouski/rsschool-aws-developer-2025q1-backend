import json
import pytest
import boto3
import os

from src.products_list import handler

def test_handler_success(dynamodb_client, lambda_context):

    dynamodb = boto3.resource('dynamodb')
    products_table = dynamodb.Table(os.environ['TABLE_NAME_PRODUCTS'])
    stocks_table = dynamodb.Table(os.environ['TABLE_NAME_STOCKS'])
    
    test_products = [
        {
            'id': '1',
            'title': 'Test Product 1',
            'description': 'Test Description 1',
            'price': 100
        },
        {
            'id': '2',
            'title': 'Test Product 2',
            'description': 'Test Description 2',
            'price': 200
        }
    ]
    
    test_stocks = [
        {
            'product_id': '1',
            'count': 5
        },
        {
            'product_id': '2',
            'count': 10
        }
    ]
    
    for product in test_products:
        products_table.put_item(Item=product)
    
    for stock in test_stocks:
        stocks_table.put_item(Item=stock)
    
    # Test the handler
    event = {}
    context = {}
    
    response = handler(event, lambda_context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert isinstance(body, list)
    assert len(body) == len(test_products)
    
    for product in body:
        assert 'id' in product
        assert 'title' in product
        assert 'description' in product
        assert 'price' in product
        assert 'count' in product

def test_handler_structure(dynamodb_client, lambda_context):

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
    
    event = {}
    context = {}
    
    response = handler(event, lambda_context)
    body = json.loads(response['body'])
    
    assert len(body) > 0
    first_product = body[0]
    assert 'id' in first_product
    assert 'title' in first_product
    assert 'description' in first_product
    assert 'price' in first_product
    assert 'count' in first_product