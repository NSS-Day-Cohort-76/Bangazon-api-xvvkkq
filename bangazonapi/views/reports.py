from django.shortcuts import render
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from bangazonapi.models import Product
from bangazonapi.models.order import Order

def expensive_products(request):
    expensive_products = Product.objects.filter(price__gte=1000)
    template = 'expensive_products.html'
    context = {
        'expensive_products': expensive_products
    }
    return render(request, template, context)

def inexpensive_products(request):
    products = Product.objects.filter(price__lte=999)
    return render(request, 'inexpensive_products.html', {'products': products})

def completed_orders(request):
    status = request.GET.get("status")  # get query param
    orders = Order.objects.all()

    # only filter if explicitly asked for "complete"
    if status == "complete":
        orders = orders.filter(payment_type__isnull=False)

    orders = orders.annotate(
        total_price=Sum(
             ExpressionWrapper(
            F('lineitems__product__price'),
            output_field=FloatField()
        )
        )
    ).select_related('customer__user', 'payment_type')

    template = 'completed_orders.html'
    context = {
        'completed_orders': orders
    }
    return render(request, template, context)
