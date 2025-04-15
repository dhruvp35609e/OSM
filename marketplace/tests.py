from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, Product, Seller
from .forms import ProductForm
from django.core.exceptions import ValidationError

class CategoryTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create a test seller
        self.seller = Seller.objects.create(
            user=self.user,
            business_name='Test Business',
            description='Test Description',
            contact_email='test@test.com',
            contact_phone='1234567890'
        )
        
        # Create test categories
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic items'
        )

    def test_category_creation(self):
        """Test that categories can be created correctly"""
        self.assertEqual(self.category.name, 'Electronics')
        self.assertEqual(self.category.slug, 'electronics')

    def test_product_form_with_valid_category(self):
        """Test product form with valid category"""
        form_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': '99.99',
            'category': self.category.id,
            'stock': 10,
            'is_active': True
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_product_form_with_invalid_category(self):
        """Test product form with invalid category ID"""
        form_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': '99.99',
            'category': 999,  # Non-existent category ID
            'stock': 10,
            'is_active': True
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)

    def test_product_form_with_no_category(self):
        """Test product form with no category selected"""
        form_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': '99.99',
            'stock': 10,
            'is_active': True
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)