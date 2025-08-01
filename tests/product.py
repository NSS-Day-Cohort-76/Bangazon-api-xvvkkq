import json
import datetime
from rest_framework import status
from rest_framework.test import APITestCase


class ProductTests(APITestCase):

    def setUp(self) -> None:
        """
        Create a new account and create sample category
        """
        url = "/register"
        data = {
            "username": "steve",
            "password": "Admin8*",
            "email": "steve@stevebrownlee.com",
            "address": "100 Infinity Way",
            "phone_number": "555-1212",
            "first_name": "Steve",
            "last_name": "Brownlee",
        }
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)
        self.token = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = "/productcategories"
        data = {"name": "Sporting Goods"}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["name"], "Sporting Goods")

    def test_create_product(self):
        """
        Ensure we can create a new product.
        """
        url = "/products"
        data = {
            "name": "Kite",
            "price": 14.99,
            "quantity": 60,
            "description": "It flies high",
            "category_id": 1,
            "location": "Pittsburgh",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["name"], "Kite")
        self.assertEqual(json_response["price"], 14.99)
        self.assertEqual(json_response["quantity"], 60)
        self.assertEqual(json_response["description"], "It flies high")
        self.assertEqual(json_response["location"], "Pittsburgh")

    def test_update_product(self):
        """
        Ensure we can update a product.
        """
        self.test_create_product()

        url = "/products/1"
        data = {
            "name": "Kite",
            "price": 24.99,
            "quantity": 40,
            "description": "It flies very high",
            "category_id": 1,
            "created_date": datetime.date.today(),
            "location": "Pittsburgh",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(url, data, format="json")
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["name"], "Kite")
        self.assertEqual(json_response["price"], 24.99)
        self.assertEqual(json_response["quantity"], 40)
        self.assertEqual(json_response["description"], "It flies very high")
        self.assertEqual(json_response["location"], "Pittsburgh")

    def test_get_all_products(self):
        """
        Ensure we can get a collection of products.
        """
        self.test_create_product()
        self.test_create_product()
        self.test_create_product()

        url = "/products"

        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 3)

    # TODO: Delete product
    def test_delete_product(self):
        """Ensure we can delete an existing product."""

        self.test_create_product()

        url = "/products/1"

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        print("Status code:", response.status_code)
        print("Response content:", response.content.decode())
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TODO: Product can be rated. Assert average rating exists.

    def test_product_rating_and_average(self):
        """
        Ensure we can rate a product and that the average rating is calculated correctly.
        """
        # First create a product
        self.test_create_product()

        # Rate the product with a rating of 4
        url = "/products/1/rate-product"  # Changed from /rate to /rate-product
        data = {"rating": 4}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create a second user to add another rating
        url = "/register"
        data2 = {
            "username": "jane",
            "password": "Admin8*",
            "email": "jane@example.com",
            "address": "200 Test Street",
            "phone_number": "555-9876",
            "first_name": "Jane",
            "last_name": "Doe",
        }
        response = self.client.post(url, data2, format="json")
        json_response = json.loads(response.content)
        token2 = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Rate the same product with a rating of 2 from the second user
        url = "/products/1/rate-product"  # Changed from /rate to /rate-product
        data = {"rating": 2}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token2)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get the product and verify the average rating
        url = "/products/1"
        response = self.client.get(url, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("average_rating", json_response)
        # Average of 4 and 2 should be 3.0
        self.assertEqual(json_response["average_rating"], 3.0)

        # Add a third rating to test the calculation further
        # Create a third user
        url = "/register"
        data3 = {
            "username": "bob",
            "password": "Admin8*",
            "email": "bob@example.com",
            "address": "300 Test Avenue",
            "phone_number": "555-5555",
            "first_name": "Bob",
            "last_name": "Smith",
        }
        response = self.client.post(url, data3, format="json")
        json_response = json.loads(response.content)
        token3 = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Rate with 5 from the third user
        url = "/products/1/rate-product"  # Changed from /rate to /rate-product
        data = {"rating": 5}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token3)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get the product again and verify the new average rating
        url = "/products/1"
        response = self.client.get(url, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("average_rating", json_response)
        # Average of 4, 2, and 5 should be 3.67 (rounded to 2 decimal places)
        expected_avg = (4 + 2 + 5) / 3
        self.assertAlmostEqual(json_response["average_rating"], expected_avg, places=2)
