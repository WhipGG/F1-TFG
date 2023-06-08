# Generated by Django 4.2.1 on 2023-06-08 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("f1dataapp", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="driver",
            name="photoUrl",
        ),
        migrations.AddField(
            model_name="driver",
            name="photo",
            field=models.ImageField(null=True, upload_to="driver_images"),
        ),
    ]
