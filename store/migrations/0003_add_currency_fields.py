
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_product_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='currency',
            field=models.CharField(choices=[('USD', 'US Dollar'), ('NGN', 'Nigerian Naira'), ('GBP', 'British Pound')], default='USD', max_length=3),
        ),
        migrations.AddField(
            model_name='order',
            name='currency',
            field=models.CharField(choices=[('USD', 'US Dollar'), ('NGN', 'Nigerian Naira'), ('GBP', 'British Pound')], default='USD', max_length=3),
        ),
    ]
