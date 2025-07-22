"""
   Author: Daniel Krusch
   Purpose: To convert product category data to json
   Methods: GET, POST
"""

"""View module for handling requests about product categories"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from bangazonapi.models import ProductCategory
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from bangazonapi.views.product import ProductSerializer


class ProductCategorySerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for product category"""
    class Meta:
        model = ProductCategory
        url = serializers.HyperlinkedIdentityField(
            view_name='productcategory',
            lookup_field='id'
        )
        fields = ('id', 'url', 'name')

class ProductCategoryWithRecentSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = ('id', 'name','products')

    def get_products(self, category):
        recent_products = category.products.order_by('-created_date')[:5]
        request = self.context.get('request')
        return ProductSerializer(recent_products, many=True, context={'request': request}).data


class ProductCategories(ViewSet):
    """Categories for products"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized product category instance
        """
        new_product_category = ProductCategory()
        new_product_category.name = request.data["name"]
        new_product_category.save()

        serializer = ProductCategorySerializer(new_product_category, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single category"""
        try:
            category = ProductCategory.objects.get(pk=pk)
            serializer = ProductCategorySerializer(category, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests to ProductCategory resource"""
        include_products = request.query_params.get('include_recent_products', None)
        
        if include_products == 'true':
            return self.categories_with_recent_products(request)
        else:
            product_category = ProductCategory.objects.all()
            serializer = ProductCategorySerializer(
                product_category, many=True, context={'request': request})
            return Response(serializer.data)
        
    def categories_with_recent_products(self, request):
        categories = ProductCategory.objects.all()
        serializer = ProductCategoryWithRecentSerializer(
            categories, many=True, context={'request': request}
        )
        return Response(serializer.data)