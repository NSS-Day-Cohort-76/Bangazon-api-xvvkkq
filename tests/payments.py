import datetime
import json
from rest_framework import status
from rest_framework.test import APITestCase


class PaymentTests(APITestCase):
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
            "last_name": "Brownlee"
        }
        response = self.client.post(url, data, format='json')
        json_response = json.loads(response.content)
        self.token = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_payment_type(self):
        """
        Ensure we can add a payment type for a customer.
        """
        url = "/payment-types"
        data = {
            "merchant_name": "American Express",
            "account_number": "111-1111-1111",
            "expiration_date": "2024-12-31",
            "create_date": datetime.date.today()
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, data, format='json')
        print("Status Code:", response.status_code)
        print("Raw Response Content:", response.content.decode())

        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["merchant_name"], "American Express")
        self.assertEqual(json_response["account_number"], "111-1111-1111")
        self.assertEqual(json_response["expiration_date"], "2024-12-31")
        self.assertEqual(json_response["create_date"], str(datetime.date.today()))

    def test_delete_payment_type(self):
        """
        Ensure we can delete an existing payment type.
        """
        # Step 1: Create a payment type
        url = "/payment-types"
        data = {
            "merchant_name": "MasterCard",
            "account_number": "333-3333-3333",
            "expiration_date": "2026-06-30",
            "create_date": datetime.date.today()
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        create_response = self.client.post(url, data, format='json')
        json_response = json.loads(create_response.content)
        payment_type_id = json_response["id"]

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Step 2: Delete it
        delete_url = f"/payment-types/{payment_type_id}"
        delete_response = self.client.delete(delete_url)

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # Step 3: Try to GET it again
        get_response = self.client.get(delete_url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
