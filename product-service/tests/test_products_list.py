import json
import pytest
from src.products_list import handler, PRODUCTS

def test_handler_success():
    event = {}
    context = {}
    
    response = handler(event, context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert isinstance(body, list)
    assert len(body) == len(PRODUCTS)
    assert body == PRODUCTS

def test_handler_structure():
    event = {}
    context = {}
    
    response = handler(event, context)
    body = json.loads(response['body'])
    
    first_product = body[0]
    assert 'id' in first_product
    assert 'title' in first_product
    assert 'description' in first_product
    assert 'price' in first_product