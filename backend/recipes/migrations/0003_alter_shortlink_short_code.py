# Generated by Django 3.2.3 on 2024-12-26 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shortlink',
            name='short_code',
            field=models.CharField(default='b3Zh', max_length=4, unique=True),
        ),
    ]
