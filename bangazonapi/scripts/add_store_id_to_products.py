import json
import random

with open('bangazonapi/fixtures/product.json', 'r') as f:
    products = json.load(f)

for product in products:
    product['fields']['store_id'] = random.randint(2, 5)

with open('bangazonapi/fixtures/product.json', 'w') as f:
    json.dump(products, f, indent=4)