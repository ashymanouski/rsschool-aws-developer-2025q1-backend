import json
import os
import boto3
import logging
from smart_open import open
import csv

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def handler(event, context):
    logger.info('Incoming event: %s', json.dumps(event))
    logger.info('Context: RequestId: %s', context.aws_request_id)
    
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            logger.info('Processing file: %s from bucket: %s', key, bucket)
            
            s3_uri = f's3://{bucket}/{key}'
            
            with open(s3_uri, 'r') as file_stream:
                csv_reader = csv.DictReader(file_stream)
                
                for row in csv_reader:
                    logger.info('Parsed record: %s', json.dumps(row))
            
            logger.info('Successfully processed file: %s', key)
            
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Successfully processed files"
            })
        }
            
    except Exception as e:
        logger.error('Error processing file: %s', str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Error processing file",
                "error": str(e)
            })
        }
