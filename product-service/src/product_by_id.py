import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table(os.environ['TABLE_NAME_PRODUCTS'])
stocks_table = dynamodb.Table(os.environ['TABLE_NAME_STOCKS'])

def handler(event, context):
    try:
        product_id = event['pathParameters']['productId']
        if not product_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing product ID"}),
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                }
            }
        
        product_response = products_table.get_item(
            Key={'id': product_id}
        )
        product = product_response.get('Item')
        
        if not product:
            return {
                'statusCode': 404,
                'headers': {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                },
                'body': json.dumps({
                    'message': 'Product not found'
                })
            }
            
        stock_response = stocks_table.get_item(
            Key={'product_id': product_id}
        )
        stock = stock_response.get('Item', {'count': '0'})
        
        joined_product = {
            'id': product['id'],
            'title': product['title'],
            'description': product['description'],
            'price': int(product['price']),
            'count': int(stock['count'])
        }
            
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps(joined_product)
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