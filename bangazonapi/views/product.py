"""View module for handling requests about products"""

import base64
from django.core.files.base import ContentFile
from django.http import HttpResponseServerError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from bangazonapi.models import Product, Customer, ProductCategory
from bangazonapi.models.recommendation import Recommendation


class ProductSerializer(serializers.ModelSerializer):
    """JSON serializer for products"""

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "number_sold",
            "description",
            "quantity",
            "created_date",
            "location",
            "image_path",
            "average_rating",
            "can_be_rated",
        )
        depth = 1


class RecommendationSerializer(serializers.ModelSerializer):
    """JSON serializer for recommendations"""

    product = ProductSerializer(read_only=True)
    recommender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Recommendation
        fields = ("id", "customer", "product", "recommender")
        read_only_fields = list("id")


class CreateRecommendationSerializer(serializers.Serializer):
    """Serializer for creating recommendations"""

    username = serializers.CharField(max_length=150)

    def validate_username(self, value):
        """Validate that the username exists"""
        try:
            user = Customer.objects.get(user__username=value)
            return value
        except Customer.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exist.")


class Products(ViewSet):
    """Request handlers for Products in the Bangazon Platform"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /products POST new product
        @apiName CreateProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {String} name Short form name of product
        @apiParam {Number} price Cost of product
        @apiParam {String} description Long form description of product
        @apiParam {Number} quantity Number of items to sell
        @apiParam {String} location City where product is located
        @apiParam {Number} category_id Category of product
        @apiParamExample {json} Input
            {
                "name": "Kite",
                "price": 14.99,
                "description": "It flies high",
                "quantity": 60,
                "location": "Pittsburgh",
                "category_id": 4
            }

        @apiSuccess (200) {Object} product Created product
        @apiSuccess (200) {id} product.id Product Id
        @apiSuccess (200) {String} product.name Short form name of product
        @apiSuccess (200) {String} product.description Long form description of product
        @apiSuccess (200) {Number} product.price Cost of product
        @apiSuccess (200) {Number} product.quantity Number of items to sell
        @apiSuccess (200) {Date} product.created_date City where product is located
        @apiSuccess (200) {String} product.location City where product is located
        @apiSuccess (200) {String} product.image_path Path to product image
        @apiSuccess (200) {Number} product.average_rating Average customer rating of product
        @apiSuccess (200) {Number} product.number_sold How many items have been purchased
        @apiSuccess (200) {Object} product.category Category of product
        @apiSuccessExample {json} Success
            {
                "id": 101,
                "url": "http://localhost:8000/products/101",
                "name": "Kite",
                "price": 14.99,
                "number_sold": 0,
                "description": "It flies high",
                "quantity": 60,
                "created_date": "2019-10-23",
                "location": "Pittsburgh",
                "image_path": null,
                "average_rating": 0,
                "category": {
                    "url": "http://localhost:8000/productcategories/6",
                    "name": "Games/Toys"
                }
            }
        """
        new_product = Product()
        new_product.name = request.data["name"]
        new_product.price = request.data["price"]
        new_product.description = request.data["description"]
        new_product.quantity = request.data["quantity"]
        new_product.location = request.data["location"]

        customer = Customer.objects.get(user=request.auth.user)
        new_product.customer = customer

        product_category = ProductCategory.objects.get(pk=request.data["category_id"])
        new_product.category = product_category

        if "image_path" in request.data:
            format, imgstr = request.data["image_path"].split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f'{new_product.id}-{request.data["name"]}.{ext}',
            )

            new_product.image_path = data

        new_product.save()

        serializer = ProductSerializer(new_product, context={"request": request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        @api {GET} /products/:id GET product
        @apiName GetProduct
        @apiGroup Product

        @apiParam {id} id Product Id

        @apiSuccess (200) {Object} product Created product
        @apiSuccess (200) {id} product.id Product Id
        @apiSuccess (200) {String} product.name Short form name of product
        @apiSuccess (200) {String} product.description Long form description of product
        @apiSuccess (200) {Number} product.price Cost of product
        @apiSuccess (200) {Number} product.quantity Number of items to sell
        @apiSuccess (200) {Date} product.created_date City where product is located
        @apiSuccess (200) {String} product.location City where product is located
        @apiSuccess (200) {String} product.image_path Path to product image
        @apiSuccess (200) {Number} product.average_rating Average customer rating of product
        @apiSuccess (200) {Number} product.number_sold How many items have been purchased
        @apiSuccess (200) {Object} product.category Category of product
        @apiSuccessExample {json} Success
            {
                "id": 101,
                "url": "http://localhost:8000/products/101",
                "name": "Kite",
                "price": 14.99,
                "number_sold": 0,
                "description": "It flies high",
                "quantity": 60,
                "created_date": "2019-10-23",
                "location": "Pittsburgh",
                "image_path": null,
                "average_rating": 0,
                "category": {
                    "url": "http://localhost:8000/productcategories/6",
                    "name": "Games/Toys"
                }
            }
        """
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product, context={"request": request})
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {"message": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response(
                {"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        """
        @api {PUT} /products/:id PUT changes to product
        @apiName UpdateProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to update
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        product = Product.objects.get(pk=pk)
        product.name = request.data["name"]
        product.price = request.data["price"]
        product.description = request.data["description"]
        product.quantity = request.data["quantity"]
        product.created_date = request.data["created_date"]
        product.location = request.data["location"]

        customer = Customer.objects.get(user=request.auth.user)
        product.customer = customer

        product_category = ProductCategory.objects.get(pk=request.data["category_id"])
        product.category = product_category
        product.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /products/:id DELETE product
        @apiName DeleteProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            product = Product.objects.get(pk=pk)
            product.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Product.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """
        @api {GET} /products GET all products
        @apiName ListProducts
        @apiGroup Product

        @apiSuccess (200) {Object[]} products Array of products
        @apiSuccessExample {json} Success
            [
                {
                    "id": 101,
                    "url": "http://localhost:8000/products/101",
                    "name": "Kite",
                    "price": 14.99,
                    "number_sold": 0,
                    "description": "It flies high",
                    "quantity": 60,
                    "created_date": "2019-10-23",
                    "location": "Pittsburgh",
                    "image_path": null,
                    "average_rating": 0,
                    "category": {
                        "url": "http://localhost:8000/productcategories/6",
                        "name": "Games/Toys"
                    }
                }
            ]
        """
        products = Product.objects.all()

        # Support filtering by category and/or quantity
        category = self.request.query_params.get("category", None)
        quantity = self.request.query_params.get("quantity", None)
        order = self.request.query_params.get("order_by", None)
        direction = self.request.query_params.get("direction", None)
        number_sold = self.request.query_params.get("number_sold", None)
        location = self.request.query_params.get("location", None)
        name = self.request.query_params.get("name", None)
        min_price = self.request.query_params.get("min_price", None)

        if order is not None:
            order_filter = order

            if direction is not None:
                if direction == "desc":
                    order_filter = f"-{order}"

            products = products.order_by(order_filter)

        if name is not None:
            products = products.filter(name__istartswith=name)

        if location is not None:
            products = products.filter(location__iexact=location)

        if category is not None:
            products = products.filter(category__id=category)

        if min_price is not None and min_price != "":
            try:
                products = products.filter(price__gte=float(min_price))
            except ValueError:
                # Handle invalid price values gracefully
                pass

        if quantity is not None:
            products = products.order_by("-created_date")[: int(quantity)]

        if number_sold is not None:

            def sold_filter(product):
                if product.number_sold >= int(number_sold):
                    return True
                return False

            products = list(filter(sold_filter, products))

        serializer = ProductSerializer(
            products, many=True, context={"request": request}
        )
        return Response(serializer.data)

    # @action(methods=['post'], detail=True)
    # def recommend(self, request, pk=None):
    #     """Recommend products to other users"""

    #     if request.method == "POST":
    #         rec = Recommendation()
    #         rec.recommender = Customer.objects.get(user=request.auth.user)
    #         rec.customer = Customer.objects.get(user__id=request.data["recipient"])
    #         rec.product = Product.objects.get(pk=pk)

    #         rec.save()

    #         return Response(None, status=status.HTTP_204_NO_CONTENT)

    #     return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    @action(methods=["post"], detail=True)
    def recommend(self, request, pk=None):
        """Recommend a product to another user"""
        try:
            # Validate the input data using the serializer
            serializer = CreateRecommendationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Get the product being recommended
            product = Product.objects.get(pk=pk)

            # Get the recommender (current user)
            recommender = Customer.objects.get(user=request.auth.user)

            # Get the recipient user by username (from validated data)
            username = serializer.validated_data["username"]
            recipient = Customer.objects.get(user__username=username)

            # Check if recommendation already exists
            existing_rec = Recommendation.objects.filter(
                recommender=recommender, customer=recipient, product=product
            ).first()

            if existing_rec:
                return Response(
                    {
                        "message": "You have already recommended this product to this user"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create the recommendation
            rec = Recommendation()
            rec.recommender = recommender
            rec.customer = recipient
            rec.product = product
            rec.save()

            # Return the created recommendation
            response_serializer = RecommendationSerializer(rec)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response(
                {"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Customer.DoesNotExist:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response(
                {"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(methods=["get"], detail=False)
    def recommendations(self, request):
        """Get recommendations for the current user"""
        try:
            customer = Customer.objects.get(user=request.auth.user)
            recommendations = Recommendation.objects.filter(customer=customer)

            # Serialize the recommended products
            recommended_products = [rec.product for rec in recommendations]
            serializer = ProductSerializer(
                recommended_products, many=True, context={"request": request}
            )

            return Response(serializer.data)

        except Customer.DoesNotExist:
            return Response(
                {"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response(
                {"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(methods=["get"], detail=False, url_path="recommendations-by-me")
    def recommendations_by_me(self, request):
        """Get recommendations made BY the current user"""
        try:
            current_user = Customer.objects.get(user=request.auth.user)
            recommendations = Recommendation.objects.filter(recommender=current_user)

            # Extract just the products from the recommendations
            products = [rec.product for rec in recommendations]
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)

        except Customer.DoesNotExist:
            return Response(
                {"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response(
                {"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
