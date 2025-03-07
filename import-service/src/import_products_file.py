import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']

def handler(event, context):
    logger.info('Incoming event: %s', json.dumps(event))
    logger.info('Context: RequestId: %s', context.aws_request_id)
    
    try:
        if not event.get('queryStringParameters') or not event['queryStringParameters'].get('name'):
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "error": "Missing 'name' parameter in query string"
                })
            }

        file_name = event['queryStringParameters']['name']
        
        signed_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': f'uploaded/{file_name}',
                'ContentType': 'text/csv'
            },
            ExpiresIn=3600
        )

        logger.info('Generated presigned URL: %s', signed_url)
        
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                 "Content-Type": "*/*"
            },
            "body": signed_url
        }
            
    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Internal server error",
                "error": str(e)
            })
        }
