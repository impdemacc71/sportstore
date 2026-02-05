from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from .models import Product, Order, OrderItem, Review
from .cart import Cart
from .forms import CartAddProductForm, OrderCreateForm, ReviewForm

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
    reviews = product.reviews.filter(is_approved=True)
    review_form = ReviewForm()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'cart_product_form': cart_product_form,
        'reviews': reviews,
        'review_form': review_form
    })

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Check if product is in stock
    if not product.is_in_stock:
        messages.error(request, f'Sorry, "{product.name}" is out of stock.')
        return redirect('product_detail', product_id=product_id)

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

def checkout(request):
    """Checkout view with Qatar address form"""
    cart = Cart(request)

    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()

            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )

                # Update stock
                product = item['product']
                product.stock -= item['quantity']
                product.update_stock_status()  # Auto-update is_in_stock
                product.save()

            # Clear the cart
            cart.clear()

            # Set order in session for success page
            request.session['order_id'] = order.id

            return redirect('order_success')
    else:
        form = OrderCreateForm()

    return render(request, 'store/checkout.html', {'cart': cart, 'form': form})

def order_success(request):
    """Order success page"""
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('product_list')

    order = get_object_or_404(Order, id=order_id)

    # Clear order_id from session
    if 'order_id' in request.session:
        del request.session['order_id']

    return render(request, 'store/order_success.html', {'order': order})

@require_POST
def add_review(request, product_id):
    """Add a product review"""
    product = get_object_or_404(Product, id=product_id)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product

        # Set user or guest name
        if request.user.is_authenticated:
            review.user = request.user
            # Use guest_name from form if provided, otherwise use username
            if not review.guest_name:
                review.guest_name = request.user.username
        else:
            # Guest review - guest_name is required
            guest_name = form.cleaned_data.get('guest_name', '').strip()
            if not guest_name:
                messages.error(request, 'Please enter your name to submit a review.')
                return redirect('product_detail', product_id=product_id)
            review.guest_name = guest_name

        review.save()
        messages.success(request, 'Your review has been submitted and will be published after approval.')
    else:
        messages.error(request, 'Please fix the errors in the form.')

    return redirect('product_detail', product_id=product_id)
