from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('category/<str:category>/', views.category, name='category'),
    path('seller/profile/<int:seller_id>/', views.seller_profile, name='seller_profile'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/become/', views.become_seller, name='become_seller'),
    path('seller/product/add/', views.add_product, name='add_product'),
    path('seller/product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('seller/product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('delete_image/<int:image_id>/', views.delete_image, name='delete_image'),
] 


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)