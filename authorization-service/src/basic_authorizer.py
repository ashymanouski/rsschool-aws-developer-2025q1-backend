import os
import base64
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

def decode_token(authorization_header: str):
    try:
        if not authorization_header or not authorization_header.strip():
            logger.warning("Empty or missing authorization header")
            return None, None

        parts = authorization_header.strip().split(' ', 1)
        
        if len(parts) != 2 or parts[0] != 'Basic':
            logger.warning("Invalid authorization header format")
            return None, None

        encoded_credentials = parts[1].strip()
        
        if not encoded_credentials:
            logger.warning("Empty credentials")
            return None, None

        try:
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            logger.info(f"Decoded credentials: '{decoded_credentials}'")
        except (base64.binascii.Error, UnicodeDecodeError):
            logger.warning("Invalid base64 encoding")
            return None, None

        logger.info(f"Checking format: contains space: {' ' in decoded_credentials}, "
                   f"contains colon: {':' in decoded_credentials}, "
                   f"equals count: {decoded_credentials.count('=')}")

        if (decoded_credentials.count('=') != 1 or 
            ' ' in decoded_credentials or 
            ':' in decoded_credentials):
            logger.warning("Invalid credentials format")
            return None, None

        username, password = decoded_credentials.split('=')

        if not username.strip() or not password.strip():
            logger.warning("Empty username or password")
            return None, None

        logger.info(f"Valid format, returning username: '{username.strip()}', "
                   f"password: '{password.strip()}'")
        return username.strip(), password.strip()

    except Exception as e:
        logger.error(f"Error decoding token: {str(e)}")
        return None, None

def handler(event, context):
    """
    Lambda authorizer handler
    Returns:
        200 - Successfully authenticated (returns Allow policy)
        401 - Missing/invalid authorization header format (throws "Unauthorized")
        403 - Valid format but invalid credentials or non-existent user (returns Deny policy)
    """
    logger.info("Event: %s", json.dumps(event))
    
    try:
        authorization_header = event.get('authorizationToken')
        logger.info(f"Authorization header: '{authorization_header}'")
        
        username, password = decode_token(authorization_header)
        
        if username is None or password is None:
            logger.info("Returning 401 - format validation failed")
            raise Exception("Unauthorized")

        stored_password = os.getenv(username)
        logger.info(f"Checking credentials for user '{username}'")
        
        if not stored_password or stored_password != password:
            logger.info(f"Returning 403 - invalid credentials for user '{username}'")
            return generate_policy(username, 'Deny', event['methodArn'])
        
        logger.info(f"Returning 200 - successful authentication for user '{username}'")
        return generate_policy(username, 'Allow', event['methodArn'])
        
    except Exception as e:
        logger.error(f"Authorization failed: {str(e)}")
        raise Exception("Unauthorized")

