# Generated by Django 4.0.2 on 2022-02-28 19:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("nutrition_tracker", "0002_userfoodportion_external_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userfoodmembership",
            name="name",
        ),
        migrations.RemoveField(
            model_name="usermeal",
            name="name",
        ),
    ]
