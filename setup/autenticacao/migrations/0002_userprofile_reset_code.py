# Generated by Django 5.0.7 on 2024-07-22 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autenticacao', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='reset_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
