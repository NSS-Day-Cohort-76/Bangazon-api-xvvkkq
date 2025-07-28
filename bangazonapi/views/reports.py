from django.shortcuts import render, get_object_or_404
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

    # Fetch favorites, optimize query with user relation
    favorites = Favorite.objects.filter(customer=customer).select_related("seller__user")

    # Get seller names from linked User model
    seller_names = [
        f"{fav.seller.user.first_name} {fav.seller.user.last_name}"
        for fav in favorites if fav.seller and fav.seller.user
    ]

    context = {
        "customer": customer,
        "sellers": seller_names
    }

    return render(request, "favorite_sellers.html", context)