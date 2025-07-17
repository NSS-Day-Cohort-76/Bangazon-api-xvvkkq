"""View module for handling requests about customer order"""

import datetime
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import action
from bangazonapi.models import Order, Payment, Customer, Product, OrderProduct
from .product import ProductSerializer


class OrderLineItemSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for line items"""

    product = ProductSerializer(many=False)

    class Meta:
        model = OrderProduct
        url = serializers.HyperlinkedIdentityField(
            view_name="lineitem", lookup_field="id"
        )
        fields = ("id", "product")
        depth = 1


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for customer orders"""

    lineitems = OrderLineItemSerializer(many=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        url = serializers.HyperlinkedIdentityField(view_name="order", lookup_field="id")
        fields = (
            "id",
            "url",
            "created_date",
            "payment_type",
            "customer",
            "lineitems",
            "total",
        )

    def get_total(self, obj):
        total = sum([li.product.price for li in obj.lineitems.all()])
        return f"{total:.2f}"


class Orders(ViewSet):
    """View for interacting with customer orders"""

    def retrieve(self, request, pk=None):
        """
        @api {GET} /cart/:id GET single order
        @apiName GetOrder
        @apiGroup Orders

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611


        @apiSuccess (200) {id} id Order id
        @apiSuccess (200) {String} url Order URI
        @apiSuccess (200) {String} created_date Date order was created
        @apiSuccess (200) {String} payment_type Payment URI
        @apiSuccess (200) {String} customer Customer URI

        @apiSuccessExample {json} Success
            {
                "id": 1,
                "url": "http://localhost:8000/orders/1",
                "created_date": "2019-08-16",
                "payment_type": "http://localhost:8000/paymenttypes/1",
                "customer": "http://localhost:8000/customers/5"
            }
        """
        try:
            customer = Customer.objects.get(user=request.auth.user)
            order = Order.objects.get(pk=pk, customer=customer)
            serializer = OrderSerializer(order, context={"request": request})
            return Response(serializer.data)

        except Order.DoesNotExist as ex:
            return Response(
                {
                    "message": "The requested order does not exist, or you do not have permission to access it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """
        @api {PUT} /order/:id PUT new payment for order
        @apiName AddPayment
        @apiGroup Orders

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Order Id route parameter
        @apiParam {id} payment_type Payment Id to pay for the order
        @apiParamExample {json} Input
            {
                "payment_type": 6
            }

        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        customer = Customer.objects.get(user=request.auth.user)
        order = Order.objects.get(pk=pk, customer=customer)
        payment_id = request.data["payment_type"]
        order.payment_type = Payment.objects.get(pk=payment_id)
        order.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        """
        @api {GET} /orders GET customer orders
        @apiName GetOrders
        @apiGroup Orders

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} payment_id Query param to filter by payment used

        @apiSuccess (200) {Object[]} orders Array of order objects
        @apiSuccess (200) {id} orders.id Order id
        @apiSuccess (200) {String} orders.url Order URI
        @apiSuccess (200) {String} orders.created_date Date order was created
        @apiSuccess (200) {String} orders.payment_type Payment URI
        @apiSuccess (200) {String} orders.customer Customer URI

        @apiSuccessExample {json} Success
            [
                {
                    "id": 1,
                    "url": "http://localhost:8000/orders/1",
                    "created_date": "2019-08-16",
                    "payment_type": "http://localhost:8000/paymenttypes/1",
                    "customer": "http://localhost:8000/customers/5"
                }
            ]
        """
        customer = Customer.objects.get(user=request.auth.user)

        orders = Order.objects.filter(customer=customer, payment_type__isnull=False)
        payment = self.request.query_params.get("payment_id", None)
        if payment is not None:
            orders = orders.filter(payment__id=payment)

        json_orders = OrderSerializer(orders, many=True, context={"request": request})

        return Response(json_orders.data)

    @action(methods=["put"], detail=True)
    def complete(self, request, pk=None):
        """Complete an order by adding a payment type"""
        try:
            # Get the order
            order = Order.objects.get(pk=pk)

            # Get the payment type from request data
            payment_type_id = request.data.get("paymentTypeId")
            payment_type = Payment.objects.get(pk=payment_type_id)

            # Complete the order by adding payment type
            order.payment_type = payment_type
            order.save()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Order.DoesNotExist:
            return Response(
                {"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Payment.DoesNotExist:
            return Response(
                {"message": "Payment type not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response(
                {"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
