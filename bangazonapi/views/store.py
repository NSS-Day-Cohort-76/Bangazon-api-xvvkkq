"""View module for handling requests about stores"""

from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from bangazonapi.models import Store, Customer, Favorite
from .customer import CustomerSerializer
from .product import ProductSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """JSON Serializer for users"""
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username']

class StoreSerializer(serializers.ModelSerializer):
    """JSON serializer for stores"""

    seller = UserSerializer(many=False)
    products = ProductSerializer(many=True, read_only=True)
    is_favorite = serializers.SerializerMethodField()


    class Meta:
        model = Store
        fields = ("id", "name", "description", "seller", "products", "is_favorite")
        depth = 1

    def get_is_favorite(self, obj):
        try:
            request = self.context.get('request')
            if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
                return False

            customer = Customer.objects.filter(user=request.user).first()
            if not customer or not obj.seller:
                return False

            return Favorite.objects.filter(customer=customer, seller=obj.seller).exists()
        except Exception:
            return False



class StoreViewSet(ViewSet):
    """Store ViewSet"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """Handle POST operations for stores"""
        try:
            store = Store()
            store.name = request.data["name"]
            store.description = request.data["description"]
            store.seller = request.user
            store.save()

            serializer = StoreSerializer(store, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single store"""
        try:
            store = Store.objects.get(pk=pk)
            serializer = StoreSerializer(store, context={"request": request})
            return Response(serializer.data)
        except Store.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for stores"""
        try:
            store = Store.objects.get(pk=pk)
            store.name = request.data["name"]
            store.description = request.data["description"]
            store.save()

            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except Store.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for stores"""
        try:
            store = Store.objects.get(pk=pk)
            store.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except Store.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests for stores"""
        try:
            stores = Store.objects.all()
            serializer = StoreSerializer(
                stores, many=True, context={"request": request}
            )
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    @action(methods=["post"], detail=True)
    def favorite(self, request, pk=None):
        """Handle POST requests to favorite a store"""
        try:
            customer = Customer.objects.get(user=request.auth.user)
            store = Store.objects.get(pk=pk)

            favorite = Favorite()
            favorite.customer = customer
            favorite.seller = store.seller
            favorite.save()

            return Response({}, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return HttpResponseServerError(ex)
