# Generated by Django 4.2.15 on 2024-10-14 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_invitations'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_image',
            field=models.ImageField(blank=True, default='images/default.svg', null=True, upload_to='images'),
        ),
    ]
