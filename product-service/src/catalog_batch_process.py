import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

products_table_name = os.environ['TABLE_NAME_PRODUCTS']
stocks_table_name = os.environ['TABLE_NAME_STOCKS']
sns_topic_arn = os.environ['SNS_TOPIC_ARN']

def handler(event, context):
    logger.info('Incoming event: %s', json.dumps(event))
    logger.info('Context: RequestId: %s', context.aws_request_id)

    try:
        products_table = dynamodb.Table(products_table_name)
        stocks_table = dynamodb.Table(stocks_table_name)

        processed_products = []
        
        for record in event['Records']:
            product_data = json.loads(record['body'])
            
            product_id = product_data['id']
            products_table.put_item(
                Item={
                    'id': product_id,
                    'title': product_data['title'],
                    'description': product_data['description'],
                    'price': product_data['price']
                }
            )
            
            stocks_table.put_item(
                Item={
                    'product_id': product_id,
                    'count': product_data['count']
                }
            )

            processed_products.append(product_data)
            
            sns.publish(
                TopicArn=sns_topic_arn,
                Subject='New Product Created',
                Message=f'New product "{product_data["title"]}" created'
            )

    except Exception as e:
        logger.error(e)
        raise