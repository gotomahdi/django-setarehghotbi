# Generated by Django 4.2.4 on 2023-09-03 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_alter_user_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile',
            field=models.ImageField(default='static/account/images/user-profile.png', null=True, upload_to='media/account', verbose_name='user profile'),
        ),
    ]
