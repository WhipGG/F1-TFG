# Generated by Django 4.2.1 on 2023-06-16 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("f1dataapp", "0004_circuit_is_recent"),
    ]

    operations = [
        migrations.AddField(
            model_name="driver",
            name="is_recent",
            field=models.BooleanField(default=False),
        ),
    ]