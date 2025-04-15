from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import  Seller, Category, ProductImage
from .forms import ProductForm, SellerForm, ProductImageForm
from django.db.models import Sum
from marketplace.models import Product


def marketplace_home(request):
    """View for the marketplace home page."""
    featured_products = Product.objects.filter(
        is_active=True,
        condition='second_hand'
    ).order_by('-created_at')[:8]

    categories = Category.objects.all()

    return render(request, 'marketplace/home.html', {
        'products': featured_products,
        'categories': categories,
    })

def category_view(request, category_slug):
    """Marketplace view for products in a specific category (only second-hand)."""
    category_obj = get_object_or_404(Category, slug=category)

    # Base query: second-hand + active + matching category
    products = Product.objects.filter(
        category=category_obj,
        is_active=True,
        condition='second_hand'
    ).order_by('-created_at')

    # Optional subcategory filter (string-based)
    subcategory = request.GET.get('subcategory')
    if subcategory:
        products = products.filter(subcategory=subcategory)  # Assuming `subcategory` is a CharField on Product

    # Optional sort filter
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-views')
    else:
        products = products.order_by('-created_at')  # Default: newest

    categories = Category.objects.all()

    return render(request, 'marketplace/home.html', {
        'products': products,
        'categories': categories,
        'current_category': category_obj,
        'current_subcategory': subcategory,
        'sort_by': sort_by,
    })
def shop(request):
    """View for the main shop page with all products."""
    products = Product.objects.filter(is_active=True,condition='new').order_by('-created_at')
    categories = Category.objects.all()
    
    # Get filter parameters
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-views')
    
    return render(request, 'marketplace/shop.html', {
        'products': products,
        'categories': categories,
    })

def category(request, category):
    """View for displaying products in a specific category."""
    category_obj = get_object_or_404(Category, slug=category)
    products = Product.objects.filter(category=category_obj, is_active=True).order_by('-created_at')
    
    # Get subcategory filter if provided
    subcategory = request.GET.get('subcategory')
    if subcategory:
        products = products.filter(subcategory=subcategory)
    
    # Get sort parameter
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-views')
    
    categories = Category.objects.all()
    
    return render(request, 'marketplace/shop.html', {
        'products': products,
        'categories': categories,
        'current_category': category_obj,
        'current_subcategory': subcategory,
    })
@login_required
def seller_profile(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    return render(request, 'marketplace/seller_profile.html', {
        'seller': seller,
    })

@login_required
def seller_dashboard(request):
    """View for the seller dashboard."""
    try:
        products = Product.objects.all()
        total_products = products.count()
        active_products = products.filter(is_active=True).count()
        total_stock = products.aggregate(total_stock=Sum('stock'))['total_stock'] or 0
        seller = Seller.objects.get(user=request.user)
        products = Product.objects.filter(seller=seller).order_by('-created_at')
        return render(request, 'marketplace/seller_dashboard.html', {
            'seller': seller,
            'products': products,
            'products': products,
            'total_products': total_products,
            'active_products': active_products,
            'total_stock': total_stock
        })
    except Seller.DoesNotExist:
            messages.info(request, 'You need to become a seller to access the dashboard.')
            return redirect('marketplace:become_seller')

@login_required
def become_seller(request):
    """View for becoming a seller."""
    if hasattr(request.user, 'seller'):
        messages.info(request, 'You are already a seller.')
        return redirect('marketplace:seller_dashboard')
    
    if request.method == 'POST':
        form = SellerForm(request.POST)
        if form.is_valid():
            seller = form.save(commit=False)
            seller.user = request.user
            seller.save()
            messages.success(request, 'Congratulations! You are now a seller.')
            return redirect('marketplace:seller_dashboard')
    else:
        form = SellerForm()
    
    return render(request, 'marketplace/become_seller.html', {'form': form})

@login_required
def add_product(request):
    """View for adding a new product with images."""

    if not hasattr(request.user, 'seller'):
        messages.error(request, 'You need to be a seller to add products.')
        return redirect('marketplace:become_seller')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        image_form = ProductImageForm(request.POST, request.FILES)

        if form.is_valid() and image_form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user.seller
            product.save()

            # Handle multiple images
            images = request.FILES.getlist('image')
            for idx, img in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=img,
                    is_primary=(idx == 0)  # First image is primary
                )

            messages.success(request, 'Product added successfully.')

            # ✅ REDIRECT BASED ON CONDITION
            if product.condition == 'new':
                return redirect('marketplace:shop')
            else:
                return redirect('marketplace:home')

        else:
            messages.error(request, 'Form is not valid. Please check the details.')

    else:
        form = ProductForm()
        image_form = ProductImageForm()

    return render(request, 'marketplace/add_product.html', {
        'form': form,
        'image_form': image_form,
    })


@login_required
def edit_product(request, product_id):
    """View for editing an existing product."""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if the user is the seller of this product
    if product.seller.user != request.user:
        messages.error(request, 'You do not have permission to edit this product.')
        return redirect('marketplace:seller_dashboard')
    
    # Handle image deletion
    if request.method == 'POST' and 'delete_image' in request.POST:
        image_id = request.POST.get('delete_image')
        try:
            image = ProductImage.objects.get(id=image_id, product=product)  # Ensure image belongs to the product
            image.delete()
            messages.success(request, 'Image deleted successfully.')
        except ProductImage.DoesNotExist:
            messages.error(request, 'Image not found or does not belong to this product.')
        return redirect('marketplace:edit_product', product_id=product.id)
    
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('marketplace:seller_dashboard')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'marketplace/edit_product.html', {
        'form': form,
        'product': product,
    })
@login_required
def delete_product(request, product_id):
    """View for deleting a product."""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if the user is the seller of this product
    if product.seller.user != request.user:
        messages.error(request, 'You do not have permission to delete this product.')
        return redirect('marketplace:seller_dashboard')
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('marketplace:seller_dashboard')
    
    return render(request, 'marketplace/delete_product.html', {'product': product})

def product_detail(request, product_id):
    """View for displaying product details."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Increment view count
    product.views += 1
    product.save()
    
    # Get related products from the same category
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).order_by('-created_at')[:4]
    
    # Fetch all images related to the product
    product_images = ProductImage.objects.filter(product=product)

    return render(request, 'marketplace/product_detail.html', {
        'product': product,
        'product_images': product_images,
        'related_products': related_products,
    })
def delete_image(request, image_id):
    """View for deleting a product image."""
    image = get_object_or_404(ProductImage, id=image_id)

    # Ensure the image belongs to the correct product
    if image.product.seller.user != request.user:
        messages.error(request, 'You do not have permission to delete this image.')
        return redirect('marketplace:seller_dashboard')
    
    # Delete the image
    image.delete()
    messages.success(request, 'Image deleted successfully.')
    
    # Redirect back to the product edit page after deletion
    return redirect('marketplace:edit_product', product_id=image.product.id)

from django.shortcuts import render, get_object_or_404
from .models import Seller, Product

def seller_profile(request, seller_id):
    # Get the seller profile by id
    seller = get_object_or_404(Seller, id=seller_id)
    
    # Get products sold by this seller
    related_products = Product.objects.filter(seller=seller)
    
    return render(request, 'marketplace/seller_profile.html', {
        'seller': seller,
        'related_products': related_products
    })
