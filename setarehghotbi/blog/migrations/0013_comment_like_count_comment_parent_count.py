# Generated by Django 4.2.4 on 2023-08-23 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_comment_have_reply'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='like_count',
            field=models.IntegerField(default=0, verbose_name='The number of likes'),
        ),
        migrations.AddField(
            model_name='comment',
            name='parent_count',
            field=models.IntegerField(default=0, verbose_name='The number of replies'),
        ),
    ]
