import json

# Map local filenames (with relative paths) to CDN URLs
cdn_image_map = {
    "vehicle.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/vehicle.jpg?updatedAt=1752870328744",
    "kia.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/1085110-8-large.jpg?updatedAt=1752870324845",
    "Untitled.png": "https://ik.imagekit.io/b0xq0alh4/Bangazon/Untitled.png?updatedAt=1752870085718",
    "91IW1wQLv-L._UY1000_.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/91IW1wQLv-L._UY1000_.jpg?updatedAt=1752870085404",
    "knife-5930548_1280.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/images%20(1).jpg?updatedAt=1752870085190",
    "fashion-1283863_1280.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/fashion-1283863_1280.jpg?updatedAt=1752870083527",
    "3902979_40__72392.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/images.jpg?updatedAt=1752870085189",
    "istockphoto-973758234-612x612.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/istockphoto-973758234-612x612.jpg?updatedAt=1752870336303",
    "t-shirt-1710578_1280.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/t-shirt-1710578_1280.jpg?updatedAt=1752870084624",
    "gloves-6872300_1280.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/gloves-6872300_1280.jpg?updatedAt=1752870084594",
    "jacket-2899728_1280.png": "https://ik.imagekit.io/b0xq0alh4/Bangazon/jacket-2899728_1280.png?updatedAt=1752870083931",
    "tool-2820944_1280.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/tool-2820944_1280.jpg?updatedAt=1752870083731",
    "jeans-564092_1280.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/jeans-564092_1280.jpg?updatedAt=1752870083653",
    "carving-4718746_1280.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/carving-4718746_1280.jpg?updatedAt=1752870083550",
    "sock-4330279_1280.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/sock-4330279_1280.jpg?updatedAt=1752870083514",
    "tool-3152370_1280.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/tool-3152370_1280.jpg?updatedAt=1752870083476",
    "cordless-drill-5471252_1280.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/cordless-drill-5471252_1280.jpg?updatedAt=1752870083468",
    "fence-2146887_1280.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/fence-2146887_1280.jpg?updatedAt=1752870083397",
    "screwdriver-655236_960_720.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/screwdriver-655236_960_720.jpg?updatedAt=1752870083344",
    "woman-6115105_1280.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/woman-6115105_1280.jpg?updatedAt=1752869814941",
    "spirit-level-1077633_1280.jpg": "https://ik.imagekit.io/b0xq0alh4/Bangazon/spirit-level-1077633_1280.jpg?updatedAt=1752880301724",
}

input_file = "bangazonapi/fixtures/product.json"
output_file = "bangazonapi/fixtures/product_cdn_updated.json"

with open(input_file, "r") as f:
    data = json.load(f)

for item in data:
    if item.get("model") == "bangazonapi.product":
        fields = item.get("fields", {})
        image_path = fields.get("image_path", "")

        # Use full relative path as key
        if image_path in cdn_image_map:
            fields["image_path"] = cdn_image_map[image_path]

with open(output_file, "w") as f:
    json.dump(data, f, indent=4)

print(f"Updated image paths saved to {output_file}")