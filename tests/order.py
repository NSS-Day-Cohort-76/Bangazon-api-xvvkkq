import json
from rest_framework import status
from rest_framework.test import APITestCase


class OrderTests(APITestCase):
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

        # Create a product category
        url = "/productcategories"
        data = {"name": "Sporting Goods"}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")

        # Create a product
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create a payment type
        url = "/payment-types"
        data = {
            "merchant_name": "Chase",
            "account_number": "1234123412341234",
            "expiration_date": "2026-07-01",
            "create_date": "2025-07-16",
            "customer_id": "1",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_product_to_order(self):
        """
        Ensure we can add a product to an order.
        """
        # Add product to order
        url = "/cart"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get cart and verify product was added
        url = "/cart"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["id"], 1)
        self.assertEqual(json_response["size"], 1)
        self.assertEqual(len(json_response["lineitems"]), 1)

    def test_remove_product_from_order(self):
        """
        Ensure we can remove a product from an order.
        """
        # Add product
        self.test_add_product_to_order()

        # Remove product from cart
        url = "/cart/1"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.delete(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get cart and verify product was removed
        url = "/cart"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["size"], 0)
        self.assertEqual(len(json_response["lineitems"]), 0)

    # TODO: Complete order by adding payment type
    def test_add_payment_type(self):
        """Ensure we can add a payment type to an order."""

        # Step 1: Add product to cart (creates the order)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post("/cart", {"product_id": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Step 2: Get the current open order
        response = self.client.get("/cart", format="json")
        json_response = json.loads(response.content)
        order_id = json_response["id"]

        # Step 3: PUT to assign payment type
        url = f"/orders/{order_id}"
        data = {"payment_type": 1}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get cart and verify payment type was added
        url = f"/orders/{order_id}"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("/payment-types/1", json_response["payment_type"])

    # TODO: New line item is not added to closed order

    def test_product_added_to_open_order_not_closed(self):
        """
        Ensure that adding a product to cart creates a new order when the previous order is closed.
        """
        # Step 1: Add product to cart (creates first order)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post("/cart", {"product_id": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Step 2: Get the first order
        response = self.client.get("/cart", format="json")
        json_response = json.loads(response.content)
        first_order_id = json_response["id"]
        self.assertEqual(json_response["size"], 1)

        # Step 3: Close the order by adding payment type
        url = f"/orders/{first_order_id}"
        data = {"payment_type": 1}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Step 4: Add another product to cart
        response = self.client.post("/cart", {"product_id": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Step 5: Get the current cart and verify it's a new order
        response = self.client.get("/cart", format="json")
        json_response = json.loads(response.content)
        second_order_id = json_response["id"]

        # Verify this is a new order (different ID) and contains the product
        self.assertNotEqual(first_order_id, second_order_id)
        self.assertEqual(json_response["size"], 1)
        self.assertEqual(len(json_response["lineitems"]), 1)

        # Verify the closed order still exists and has payment type
        response = self.client.get(f"/orders/{first_order_id}", format="json")
        closed_order = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("/payment-types/1", closed_order["payment_type"])

    # TODO: The next Test HEHE :)
