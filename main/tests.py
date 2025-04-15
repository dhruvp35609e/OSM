from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Cart, CartItem
from marketplace.models import Product
from django.contrib.auth import get_user_model

class CartViewTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        
        # Create a test product
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=10.00,
            stock=10
        )

    def test_cart_view_requires_login(self):
        """Test that cart view requires login"""
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertTrue(response.url.startswith('/login/'))

    def test_cart_view_logged_in(self):
        """Test that cart view works when logged in"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart.html')

    def test_cart_creation(self):
        """Test that cart is created for user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('cart'))
        self.assertTrue(Cart.objects.filter(user=self.user).exists())

    def test_add_to_cart(self):
        """Test adding item to cart"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('add_to_cart', args=[self.product.id]))
        cart = Cart.objects.get(user=self.user)
        self.assertTrue(CartItem.objects.filter(cart=cart, product=self.product).exists())