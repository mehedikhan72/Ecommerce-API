# Generated by Django 4.2 on 2023-05-09 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_alter_review_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='avg_rating',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='total_ratings',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]