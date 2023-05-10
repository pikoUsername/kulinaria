# Generated by Django 4.2.1 on 2023-05-10 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foodingredients',
            name='ingredient',
        ),
        migrations.AddField(
            model_name='foodingredients',
            name='ingredient',
            field=models.ManyToManyField(to='foods.ingredients'),
        ),
    ]
