# Generated by Django 5.0.6 on 2024-05-20 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syatemd', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='shiiregyosha',
            fields=[
                ('shiireid', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('shiiremei', models.CharField(max_length=64)),
                ('shiireaddress', models.CharField(max_length=64)),
                ('shiiretel', models.CharField(max_length=13)),
                ('shihonkin', models.IntegerField()),
                ('nouki', models.IntegerField()),
            ],
        ),
    ]