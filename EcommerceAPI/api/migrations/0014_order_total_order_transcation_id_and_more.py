# Generated by Django 4.2 on 2023-05-06 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_order_outside_comilla_order_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='order',
            name='transcation_id',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(default='online', max_length=100),
        ),
    ]