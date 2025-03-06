# AWS DynamoDB Table Population Script
# ----------------------------------
# Requirements:
# - Python 3.x
# - boto3 (`pip install boto3`)
# - Configured AWS CLI with valid profile
# - Existing DynamoDB tables: 'products' and 'stocks'

# Usage:
# python add_products.py <aws-profile-name>

# Example:
# python add_products.py rs_school_aws_dev

# Description:
# Script populates DynamoDB tables with test data for an audio equipment store. Creates 10 products with random stock counts (1-50) using provided AWS profile credentials.


import boto3
import uuid
import sys
import random


if len(sys.argv) != 2:
    # Wrong number of arguments
    if len(sys.argv) < 2:
        print("Error: No profile name provided")
    else:
        print("Error: Too many arguments")
    
    print("Please provide AWS profile name!")
    print("Usage: python script.py profile_name")
    sys.exit(1)

profile_name = sys.argv[1]
print(f"Using profile: {profile_name}")

session = boto3.Session(profile_name=profile_name)
dynamodb = session.resource('dynamodb')

products_table = dynamodb.Table('products')
stocks_table = dynamodb.Table('stocks')

products = [
    {
        "title": "Bose QuietComfort Earbuds II",
        "description": "Wireless Noise Cancelling Earbuds",
        "price": 229
    },
    {
        "title": "Apple AirPods Pro",
        "description": "Active Noise Cancellation, Transparency Mode",
        "price": 249
    },
    {
        "title": "Sony WH-1000XM4",
        "description": "Wireless Noise Cancelling Over-Ear Headphones",
        "price": 349
    },
    {
        "title": "Samsung Galaxy Buds Pro",
        "description": "Intelligent ANC, 360 Audio",
        "price": 199
    },
    {
        "title": "Jabra Elite 85t",
        "description": "Advanced ANC, Wireless Charging",
        "price": 179
    },
    {
        "title": "Beats Fit Pro",
        "description": "Secure Fit, Active Noise Cancelling",
        "price": 199
    },
    {
        "title": "Sennheiser Momentum True Wireless 3",
        "description": "High-Quality Sound, ANC",
        "price": 299
    },
    {
        "title": "Anker Soundcore Liberty 3 Pro",
        "description": "Personalized Sound, LDAC Codec",
        "price": 169
    },
    {
        "title": "Google Pixel Buds Pro",
        "description": "Google Assistant Integration, ANC",
        "price": 199
    },
    {
        "title": "Nothing Ear (2)",
        "description": "Transparent Design, Hybrid ANC",
        "price": 149
    }
]

print("Starting to add products...")

for product in products:
    id = str(uuid.uuid4())
    products_table.put_item(
        Item={
            'id': id,
            'title': product['title'],
            'description': product['description'],
            'price': product['price']
        }
    )
    print(f"Added product: {product['title']}")
    

    stock_count = random.randint(1, 100)
    stocks_table.put_item(
        Item={
            'product_id': id,
            'count': stock_count
        }
    )
    print(f"Added stock for: {product['title']} (Count: {stock_count})")

print("Done!")