import json
import os
import pytest
from src.import_file_parser import handler

def test_successful_file_processing(s3_client, valid_csv_content):
    """Test successful processing of a valid CSV file"""
    bucket_name = os.environ['BUCKET_NAME']
    
    s3_client.put_object(
        Bucket=bucket_name,
        Key='uploaded/test.csv',
        Body=valid_csv_content
    )
    
    event = {
        'Records': [{
            's3': {
                'bucket': {'name': bucket_name},
                'object': {'key': 'uploaded/test.csv'}
            }
        }]
    }
    
    context = type('obj', (object,), {
        'aws_request_id': 'test-request-id'
    })
    
    response = handler(event, context)
    
    assert response['statusCode'] == 200
    assert response['headers']['Access-Control-Allow-Origin'] == '*'
    assert response['headers']['Content-Type'] == 'application/json'
    assert json.loads(response['body'])['message'] == 'Successfully processed files'
    
    objects = s3_client.list_objects_v2(Bucket=bucket_name)
    keys = [obj['Key'] for obj in objects.get('Contents', [])]
    assert 'parsed/test.csv' in keys
    assert 'uploaded/test.csv' not in keys