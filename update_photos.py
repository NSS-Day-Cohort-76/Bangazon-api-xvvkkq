import json

# Load the JSON data
with open('bangazonapi/fixtures/product.json', 'r') as f:
    data = json.load(f)

# Update image_path
for item in data:
    if item['model'] == 'bangazonapi.product':
        fields = item['fields']
        name = fields.get('name', '')
        description = fields.get('description', '')

        # Volkswagen Golf update
        if name == 'Golf' and 'Volkswagen' in description:
            fields['image_path'] = 'products/vehicle.jpg'

        # Kia Optima update
        if name == 'Optima' and 'Kia' in description:
            fields['image_path'] = 'products/kia.jpg'

# Save updated JSON to a new file
with open('bangazonapi/fixtures/products_updated.json', 'w') as f:
    json.dump(data, f, indent=4)

print("Updated image_path for Volkswagen Golf and Kia Optima products only.")