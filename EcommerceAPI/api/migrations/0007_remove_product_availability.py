# Generated by Django 4.1.1 on 2023-04-16 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_product_availability'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='availability',
        ),
    ]