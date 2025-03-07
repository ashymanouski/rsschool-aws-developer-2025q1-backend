import pytest
import json
from src.import_products_file import handler

def test_import_products_file_success(s3_client):
    event = {
        'queryStringParameters': {
            'name': 'test.csv'
        }
    }
    context = type('obj', (object,), {
        'aws_request_id': 'test-request-id'
    })

    response = handler(event, context)

    assert response['statusCode'] == 200
    assert response['headers']['Access-Control-Allow-Origin'] == '*'
    assert isinstance(response['body'], str)
    assert 'uploaded/test.csv' in response['body']

@pytest.mark.parametrize(
    "event,expected_status,expected_error",
    [
        (
            {},
            400,
            "Missing 'name' parameter in query string"
        ),
        (
            {'queryStringParameters': {}},
            400,
            "Missing 'name' parameter in query string"
        ),
        (
            {'queryStringParameters': {'wrong': 'param'}},
            400,
            "Missing 'name' parameter in query string"
        ),
        (
            {'queryStringParameters': {'name': ''}},
            400,
            "Missing 'name' parameter in query string"
        ),
    ],
    ids=[
        "completely_empty_event",
        "event_with_empty_query_parameters",
        "event_with_incorrect_parameter_name",
        "event_with_empty_name"
    ]
)
def test_import_products_file_validation(event, expected_status, expected_error):
    """Test various invalid input scenarios for the import products file handler"""
    context = type('obj', (object,), {
        'aws_request_id': 'test-request-id'
    })

    response = handler(event, context)

    assert response['statusCode'] == expected_status

    error_body = json.loads(response['body'])
    assert error_body['error'] == expected_error

    assert 'headers' in response
    assert 'Access-Control-Allow-Origin' in response['headers']
