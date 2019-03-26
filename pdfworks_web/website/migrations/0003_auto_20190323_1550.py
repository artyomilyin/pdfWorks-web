# Generated by Django 2.1.7 on 2019-03-23 12:50

from django.db import migrations, models
import website.models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_auto_20190322_2309'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='uploadedfile',
            options={'ordering': ('-id',)},
        ),
        migrations.AlterField(
            model_name='uploadedfile',
            name='filename',
            field=models.FileField(upload_to=website.models.UploadedFile.define_upload_path),
        ),
    ]