# Generated by Django 2.1.4 on 2019-01-01 04:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('doofen', '0011_auto_20190101_0327'),
    ]

    operations = [
        #migrations.CreateModel(
        #    name='TeacherAccount',
        #    fields=[
        #        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #        ('username', models.CharField(max_length=25)),
        #        ('password', models.CharField(max_length=32)),
        #        ('classnum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doofen.Classnum')),
        #    ],
        #),
        migrations.AddField(
            model_name='exam',
            name='off_line',
            field=models.BooleanField(default=False),
        ),
        #migrations.AddField(
        #    model_name='session',
        #    name='classnum',
        #    field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='doofen.Classnum'),
        #),
    ]
