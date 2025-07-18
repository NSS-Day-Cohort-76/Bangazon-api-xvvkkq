import json

# Load the JSON data
with open('bangazonapi/fixtures/product.json', 'r') as f:
    data = json.load(f)

# Update image_path only for Golf Volkswagens
for item in data:
    if item['model'] == 'bangazonapi.product':
        fields = item['fields']
        name = fields.get('name', '')
        description = fields.get('description', '')
        
        if name == 'Golf' and 'Volkswagen' in description:
            # Change to the desired image path
            fields['image_path'] = 'products/vehicle.jpg'

# Save updated JSON to a new file
with open('bangazonapi/fixtures/products_updated.json', 'w') as f:
    json.dump(data, f, indent=4)

print("Updated image_path for Volkswagen Golf products only.")