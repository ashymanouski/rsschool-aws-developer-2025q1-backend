import json
import os
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table(os.environ['TABLE_NAME_PRODUCTS'])
stocks_table = dynamodb.Table(os.environ['TABLE_NAME_STOCKS'])

def validate_product(body):
    errors = []
    
    required_fields = ['title', 'description', 'price', 'count']
    missing_fields = [field for field in required_fields if field not in body]
    if missing_fields:
        errors.append(f"Missing required fields: {', '.join(missing_fields)}")
        return errors
    
    try:
        if int(body['price']) <= 0:
            errors.append("Price must be positive")
    except ValueError:
        errors.append("Price must be a number")
        
    try:
        if int(body['count']) < 0:
            errors.append("Count must be non-negative")
    except ValueError:
        errors.append("Count must be a number")
        
    if not body['title'].strip():
        errors.append("Title cannot be empty")
    if not body['description'].strip():
        errors.append("Description cannot be empty")
        
    return errors

def handler(event, context):
    try:
        if not event.get('body'):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing request body"}),
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                }
            }
            
        body = json.loads(event['body'])
        
        validation_errors = validate_product(body)
        if validation_errors:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "error": "Validation failed",
                    "details": validation_errors
                })
            }
            
        product_id = str(uuid.uuid4())
        
        product = {
            'id': product_id,
            'title': body['title'].strip(),
            'description': body['description'].strip(),
            'price': int(body['price'])
        }
        
        stock = {
            'product_id': product_id,
            'count': int(body['count'])
        }
        
        products_table.put_item(Item=product)
        stocks_table.put_item(Item=stock)
        
        response_item = {
            **product,
            'count': stock['count']
        }
            
        return {
            'statusCode': 201,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps(response_item)
        }
    except ValueError as ve:
        return {
            'statusCode': 400,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({
                'message': 'Invalid request body',
                'error': str(ve)
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({
                'message': 'Internal server error',
                'error': str(e)
            })
        }