# Generated by Django 2.2 on 2021-08-27 03:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login_registration_app', '0002_auto_20210810_1352'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Users',
            new_name='User',
        ),
    ]
