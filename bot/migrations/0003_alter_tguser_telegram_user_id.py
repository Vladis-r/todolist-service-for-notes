# Generated by Django 4.1.4 on 2023-01-10 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_remove_tguser_user_id_tguser_telegram_user_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tguser',
            name='telegram_user_id',
            field=models.PositiveSmallIntegerField(unique=True),
        ),
    ]
