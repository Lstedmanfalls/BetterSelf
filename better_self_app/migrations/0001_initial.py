# Generated by Django 2.2 on 2021-09-02 22:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('login_registration_app', '0003_auto_20210826_2139'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote', models.TextField()),
                ('author', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_who_uploaded', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quote_uploader', to='login_registration_app.User')),
            ],
        ),
    ]