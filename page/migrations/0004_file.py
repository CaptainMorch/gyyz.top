# Generated by Django 2.1.3 on 2018-12-04 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0003_board_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('f', models.FileField(upload_to='')),
            ],
        ),
    ]
