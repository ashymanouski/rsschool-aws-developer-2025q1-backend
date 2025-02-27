import json
import os
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table(os.environ['TABLE_NAME_PRODUCTS'])
stocks_table = dynamodb.Table(os.environ['TABLE_NAME_STOCKS'])

def handler(event, context):
    try:
        # Parse the request body
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
        
        # Validate required fields
        required_fields = ['title', 'description', 'price', 'count']
        missing_fields = [field for field in required_fields if field not in body]
        
        if missing_fields:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }),
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                }
            }
            
        # Generate a new product ID
        product_id = str(uuid.uuid4())
        
        # Create product entry
        product = {
            'id': product_id,
            'title': body['title'],
            'description': body['description'],
            'price': int(body['price']),
            'createdAt': datetime.utcnow().isoformat()
        }
        
        # Create stock entry
        stock = {
            'product_id': product_id,
            'count': int(body['count'])
        }
        
        # Save to DynamoDB
        products_table.put_item(Item=product)
        stocks_table.put_item(Item=stock)
        
        # Combine product and stock for response
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
