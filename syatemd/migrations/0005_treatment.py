# Generated by Django 5.0.6 on 2024-06-05 05:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syatemd', '0004_medicine'),
    ]

    operations = [
        migrations.CreateModel(
            name='Treatment',
            fields=[
                ('treatment_id', models.AutoField(primary_key=True, serialize=False)),
                ('dosage', models.IntegerField()),
                ('status', models.CharField(default='pending', max_length=10)),
                ('empid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='syatemd.employee')),
                ('medicineid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='syatemd.medicine')),
                ('patid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='syatemd.paitent')),
            ],
        ),
    ]