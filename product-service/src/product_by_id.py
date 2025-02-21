import json

PRODUCTS = [
    {"id": "1", "title": "Bose QuietComfort Earbuds II", "description": "Wireless Noise Cancelling Earbuds", "price": 229},
    {"id": "2", "title": "Apple AirPods Pro", "description": "Active Noise Cancellation, Transparency Mode", "price": 249},
    {"id": "3", "title": "Sony WH-1000XM4", "description": "Wireless Noise Cancelling Over-Ear Headphones", "price": 349},
    {"id": "4", "title": "Samsung Galaxy Buds Pro", "description": "Intelligent ANC, 360 Audio", "price": 199},
    {"id": "5", "title": "Jabra Elite 85t", "description": "Advanced ANC, Wireless Charging", "price": 179},
    {"id": "6", "title": "Beats Fit Pro", "description": "Secure Fit, Active Noise Cancelling", "price": 199},
    {"id": "7", "title": "Sennheiser Momentum True Wireless 3", "description": "High-Quality Sound, ANC", "price": 299},
    {"id": "8", "title": "Anker Soundcore Liberty 3 Pro", "description": "Personalized Sound, LDAC Codec", "price": 169},
    {"id": "9", "title": "Google Pixel Buds Pro", "description": "Google Assistant Integration, ANC", "price": 199},
    {"id": "10", "title": "Nothing Ear (2)", "description": "Transparent Design, Hybrid ANC", "price": 149}
]

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
        
        product = next(
            (product for product in PRODUCTS if product['id'] == product_id),
            None
        )
        
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
            
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps(product)
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