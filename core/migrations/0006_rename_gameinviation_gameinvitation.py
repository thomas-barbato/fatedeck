# Generated by Django 3.2.18 on 2023-05-20 22:32

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_loggedinuser"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Gameinviation",
            new_name="Gameinvitation",
        ),
    ]
