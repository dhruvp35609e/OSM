from django import forms
from .models import Category, Product, Seller, ProductImage

class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['business_name', 'description', 'contact_email', 'contact_phone']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select a category",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'price','condition', 'stock', 'category', 'is_active']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get all available categories
        categories = Category.objects.all().order_by('name')
        if not categories.exists():
            # If no categories exist, display a more helpful message
            self.fields['category'].empty_label = "No categories available - please contact admin"
        else:
            self.fields['category'].queryset = categories
            self.fields['category'].empty_label = "Select a category"
        
    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError("Please select a valid category.")
        # Verify that the category exists in the database
        try:
            return Category.objects.get(pk=category.pk)
        except Category.DoesNotExist:
            raise forms.ValidationError("The selected category is not valid. Please choose from the available options.")

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary']
# class MarketplaceProductForm(forms.ModelForm):
#     CATEGORY_CHOICES = [
#         ('electronics', 'Electronics'),
#         ('clothes', 'Clothes'),
#         ('books', 'Books'),
#         ('home_appliances', 'Home Appliances'),
#         ('sports', 'Sports'),
#     ]
#     category = forms.ChoiceField(choices=CATEGORY_CHOICES)

#     class Meta:
#         model = MarketplaceProduct
#         fields = ['name', 'description', 'price', 'stock', 'category', 'image', 'is_active']