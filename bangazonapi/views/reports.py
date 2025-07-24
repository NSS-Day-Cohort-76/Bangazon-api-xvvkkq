from django.shortcuts import render
from bangazonapi.models import Product

def expensive_products(request):
    expensive_products = Product.objects.filter(price__gte=1000)
    template = 'expensive_products.html'
    context = {
        'expensive_products': expensive_products
    }
    return render(request, template, context)
