# Generated by Django 4.2.7 on 2023-11-06 04:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("teachers", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="grade",
            name="grade",
            field=models.DecimalField(decimal_places=2, max_digits=5, null=True),
        ),
    ]