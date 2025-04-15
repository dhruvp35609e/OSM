from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import login,logout
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import  Category, Cart, CartItem, Order, OrderItem
from marketplace.models import Product
def home(request):
    featured_products = Product.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()[:4]
    random_products = Product.objects.filter(is_active=True).order_by('?')[:4]

    return render(request, 'home.html', {
        'featured_products': featured_products,
        'categories': categories,
        'random_products': random_products
    })
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to OSM.')
            return redirect('home')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
from django.http import HttpResponse

def test_login(request):
    from django.contrib.auth.models import User
    user = authenticate(username='yourtestuser', password='thepassword')
    if user is not None:
        login(request, user)
        return HttpResponse(f"Logged in as {user.username}")
    else:
        return HttpResponse("Failed to log in.")
def login_view(request):
    print("Login view called")
    if request.method == 'POST':
        print("POST request received")
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)  # <-- fixed this line
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def products(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, 'products.html', {
        'products': products,
        'categories': categories
    })

def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)
    categories = Category.objects.all()
    return render(request, 'category.html', {
        'category': category,
        'products': products,
        'categories': categories
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products
    })

@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('some-safe-page')  # Change this to a valid redirect destination

    # Step 2: Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Step 3: Try adding the product to the cart, handle IntegrityError if product/cart relationship fails
    try:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    except IntegrityError:
        messages.error(request, "Something went wrong adding the product to cart.")
        return redirect('cart')

    # Step 4: If the product was already in the cart, increase quantity
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Step 5: Success message
    messages.success(request, f"{product.name} added to your cart.")
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from your cart.')
    return redirect('cart')

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated successfully.')
    else:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    
    return redirect('cart')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if request.method == 'POST':
        # In a real application, you would process payment here
        # For this example, we'll just create an order
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.total_price,
            shipping_address=request.POST.get('shipping_address'),
            payment_method=request.POST.get('payment_method')
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        # Clear the cart
        cart.items.all().delete()
        
        messages.success(request, 'Order placed successfully!')
        return redirect('order_confirmation', order_id=order.id)
    
    return render(request, 'checkout.html', {'cart': cart})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'orders': orders})

@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})

class LogoutViaGet(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')