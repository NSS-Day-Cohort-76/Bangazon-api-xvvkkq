"""View module for handling requests about stores"""

from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from bangazonapi.models import Store, Customer, Favorite
from .customer import CustomerSerializer


class StoreSerializer(serializers.ModelSerializer):
    """JSON serializer for stores"""

    seller = CustomerSerializer(many=False)

    class Meta:
        model = Store
        fields = ("id", "name", "description", "seller")
        depth = 1


class StoreViewSet(ViewSet):
    """Store ViewSet"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """Handle POST operations for stores"""
        try:
            customer = Customer.objects.get(user=request.auth.user)
            store = Store()
            store.name = request.data["name"]
            store.description = request.data["description"]
            store.seller = customer
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
