# Generated by Django 4.2 on 2023-05-10 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_alter_product_avg_rating_alter_product_total_ratings_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sold',
            field=models.IntegerField(default=0),
        ),
    ]
