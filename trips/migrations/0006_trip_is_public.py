# Generated by Django 5.2.1 on 2025-05-26 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0005_alter_trippoint_options_remove_trippoint_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='is_public',
            field=models.BooleanField(default=True, verbose_name='Публичный маршрут'),
        ),
    ]
