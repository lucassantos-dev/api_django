# Generated by Django 4.2.3 on 2023-07-24 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_useraccount_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
    ]