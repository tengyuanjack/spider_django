# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spider', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentnew',
            name='comment_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='commentnew',
            name='comment_date',
            field=models.CharField(default=1968, max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='commentnew',
            name='hasReply',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='commentnew',
            name='help',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='commentnew',
            name='sugg_sen_neg',
            field=models.DecimalField(default=0, max_digits=20, decimal_places=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='commentnew',
            name='sugg_sen_pos',
            field=models.DecimalField(default=0, max_digits=20, decimal_places=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='commentsentiment',
            name='comment_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
