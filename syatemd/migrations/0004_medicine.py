# Generated by Django 5.0.6 on 2024-05-31 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syatemd', '0003_paitent'),
    ]

    operations = [
        migrations.CreateModel(
            name='medicine',
            fields=[
                ('medicineid', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('medicinename', models.CharField(max_length=64)),
                ('unit', models.CharField(max_length=64)),
            ],
        ),
    ]