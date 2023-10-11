# Generated by Django 4.2.5 on 2023-10-04 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0002_remove_myclass_teacher_name_remove_discussion_course_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='Num1',
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AddField(
            model_name='quiz',
            name='Num2',
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AddField(
            model_name='quiz',
            name='Num3',
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AddField(
            model_name='quiz',
            name='Num4',
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AddField(
            model_name='quiz',
            name='correct_answer',
            field=models.IntegerField(choices=[(1, 'Num 1'), (2, 'Num 2'), (3, 'Num 3'), (4, 'Num 4')], default=None),
        ),
        migrations.DeleteModel(
            name='Question',
        ),
    ]
