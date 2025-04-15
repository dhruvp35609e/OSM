from django.db import migrations
from django.utils.text import slugify

def create_default_categories(apps, schema_editor):
    Category = apps.get_model('marketplace', 'Category')
    default_categories = [
        ('Electronics', 'electronics'),
        ('Clothes', 'clothes'),
        ('Books', 'books'),
        ('Home Appliances', 'home_appliances'),
        ('Sports', 'sports'),
    ]
    
    for name, slug in default_categories:
        Category.objects.get_or_create(
            name=name,
            slug=slug,
            defaults={'description': f'Category for {name.lower()}'}
        )

def remove_default_categories(apps, schema_editor):
    Category = apps.get_model('marketplace', 'Category')
    Category.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_categories, remove_default_categories),
    ]