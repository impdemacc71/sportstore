from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Product
from .cart import Cart
from .forms import CartAddProductForm

def product_list(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.all()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    return render(request, 'store/product_list.html', {'products': products, 'query': query})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_product_form = CartAddProductForm()
    return render(request, 'store/product_detail.html', {'product': product,
                                                          'cart_product_form': cart_product_form})

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
    return redirect('cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'],
                                                                   'override': True})
    return render(request, 'store/cart_detail.html', {'cart': cart})
