import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table(os.environ['TABLE_NAME_PRODUCTS'])
stocks_table = dynamodb.Table(os.environ['TABLE_NAME_STOCKS'])

def handler(event, context):
    logger.info('Incoming event: %s', json.dumps(event))
    logger.info('Context: RequestId: %s', context.aws_request_id)
    
    try:
        products_response = products_table.scan()
        products = products_response['Items']
        
        stocks_response = stocks_table.scan()
        stocks = stocks_response['Items']
        
        stock_by_product_id = {
            stock['product_id']: int(stock['count'])
            for stock in stocks
        }
        
        joined_products = []
        for product in products:
            joined_product = {
                'id': product['id'],
                'title': product['title'],
                'description': product['description'],
                'price': int(product['price']),
                'count': stock_by_product_id.get(product['id'], 0)
            }
            joined_products.append(joined_product)
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps(joined_products)
        }
    except Exception as e:
        error_message = str(e)
        logger.error('Unexpected error occurred: %s', error_message)
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({
                'message': 'Internal server error',
                'error': error_message
            })
        }