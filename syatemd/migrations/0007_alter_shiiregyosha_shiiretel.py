# Generated by Django 5.0.6 on 2024-06-13 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syatemd', '0006_treatment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shiiregyosha',
            name='shiiretel',
            field=models.CharField(max_length=20),
        ),
    ]