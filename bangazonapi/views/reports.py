from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from bangazonapi.models import Product, Favorite, Customer
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
    context = {"orders": orders}
    return render(request, template, context)


def favorite_sellers(request):
    customer_id = request.GET.get("customer")

    if not customer_id:
        return render(request, "reports/error.html", {
            "message": "Customer ID is required."
        })

    try:
        customer_id = int(customer_id)
    except ValueError:
        return render(request, "reports/error.html", {
            "message": "Customer ID must be an integer."
        })

    customer = get_object_or_404(Customer, id=customer_id)
    favorites = Favorite.objects.filter(customer=customer).select_related("seller__user")
    
    seller_names = [
        f"{fav.seller.user.first_name} {fav.seller.user.last_name}"
        for fav in favorites if fav.seller and fav.seller.user
    ]

    context = {
        "customer": customer,
        "sellers": seller_names
    }

    return render(request, "favorite_sellers.html", context)