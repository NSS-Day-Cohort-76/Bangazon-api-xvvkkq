from django.shortcuts import render
from bangazonapi.models import Product, Favorite, Customer

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


def favorite_sellers(request):
    customer_id = request.GET.get("customer")

    # Validate query parameter
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

    customer = Customer.objects.filter(id=customer_id).first()
    if not customer:
        return render(request, "reports/error.html", {
            "message": f"No customer found with ID {customer_id}."
        })

    favorites = Favorite.objects.filter(customer=customer).select_related("seller")
    seller_names = [fav.seller.name for fav in favorites if fav.seller is not None]

    context = {
        "customer": customer,
        "sellers": seller_names
    }

    return render(request, "reports/favorite_sellers.html", context)