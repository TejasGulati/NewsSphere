# Generated by Django 5.0.8 on 2024-08-17 14:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_alter_notification_article'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='article',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='article_url',
        ),
    ]
