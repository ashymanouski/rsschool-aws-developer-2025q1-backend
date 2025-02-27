# tests/test_product_by_id.py
import json
import pytest
from src.product_by_id import handler, PRODUCTS

def test_get_existing_product():
    event = {
        'pathParameters': {
            'productId': '1'
        }
    }
    context = {}
    
    response = handler(event, context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['id'] == '1'
    assert body == PRODUCTS[0]

def test_product_not_found():
    event = {
        'pathParameters': {
            'productId': 'non-existent'
        }
    }
    context = {}
    
    response = handler(event, context)
    
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert body['message'] == 'Product not found'

def test_invalid_request():
    event = {}
    context = {}
    
    response = handler(event, context)
    
    assert response['statusCode'] == 500