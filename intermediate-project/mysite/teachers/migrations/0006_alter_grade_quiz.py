# Generated by Django 4.2.6 on 2023-11-07 03:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("teachers", "0005_alter_grade_grade"),
    ]

    operations = [
        migrations.AlterField(
            model_name="grade",
            name="quiz",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="teachers.quiz"
            ),
        ),
    ]
