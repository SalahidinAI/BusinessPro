# Generated by Django 5.1.4 on 2025-02-27 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('richman', '0017_alter_group_unique_together'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='group',
            constraint=models.UniqueConstraint(fields=('owner', 'group_date'), name='unique_owner_group_date'),
        ),
    ]
