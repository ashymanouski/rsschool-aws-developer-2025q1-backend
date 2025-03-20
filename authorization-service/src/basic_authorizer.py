import os
import base64
import json

def generate_policy(principal_id: str, effect: str, resource: str):
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
    }

def decode_token(encoded_credentials: str):
    try:
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split('=')
        return username, password
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        return None, None

def handler(event, context):
    """
    Lambda handler for basic authorization
    """
    print("Event:", json.dumps(event))
    
    try:
        authorization_header = event.get('authorizationToken')
        
        if not authorization_header:
            print("No authorization token present")
            return {
                'statusCode': 401,
                'body': json.dumps('Unauthorized: No authorization token')
            }
        
        username, password = decode_token(authorization_header)
        
        if not username or not password:
            print("Invalid token format")
            return {
                'statusCode': 401,
                'body': json.dumps('Unauthorized: Invalid token format')
            }
        
        stored_password = os.getenv(username)
        
        if not stored_password or stored_password != password:
            print(f"Access denied for user: {username}")
            return {
                'statusCode': 403,
                'body': json.dumps('Forbidden: Invalid credentials')
            }
        
        resource = event['methodArn']
        policy = generate_policy(username, 'Allow', resource)
        
        print(f"Successfully authenticated user: {username}")
        return policy
        
    except Exception as e:
        print(f"Error in authorization: {str(e)}")
        return {
            'statusCode': 401,
            'body': json.dumps(f'Unauthorized: {str(e)}')
        }
