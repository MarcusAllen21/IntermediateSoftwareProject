# Generated by Django 4.2.6 on 2023-11-07 04:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("teachers", "0006_alter_grade_quiz"),
    ]

    operations = [
        migrations.AlterField(
            model_name="grade",
            name="grade",
            field=models.DecimalField(decimal_places=2, default=-1.0, max_digits=5),
        ),
    ]