# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spider', '0002_auto_20160427_1043'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernew',
            name='cid',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
