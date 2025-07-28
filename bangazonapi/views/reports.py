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

def orders_report(request):
    status = request.GET.get("status")

    orders = Order.objects.all()

    if status == "complete":
        orders = orders.filter(payment_type__isnull=False)
    elif status == "incomplete":
        orders = orders.filter(payment_type__isnull=True)
    else:
        orders = []

    print(f"STATUS: {status}")
    print(f"ORDERS: {orders}")
    print(f"Orders BEFORE annotate: {orders.count()}")    

    orders = orders.annotate(
        total_cost=Sum(                
            ExpressionWrapper(
                F("lineitems__product__price"),
                output_field=FloatField()
            )
        )
    ).select_related("customer__user")

    print(f"Orders AFTER annotate: {orders.count()}")

    template = "incomplete_orders.html" if status == "incomplete" else "completed_orders.html"
    context = {"completed_orders": orders}
    return render(request, template, context)