# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommentNew',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pid', models.IntegerField()),
                ('user_url', models.CharField(max_length=200)),
                ('user_name', models.CharField(max_length=100)),
                ('star', models.CharField(max_length=20)),
                ('suggestion', models.CharField(max_length=200)),
                ('isConfirmed', models.IntegerField()),
                ('comment', models.TextField()),
                ('hasImage', models.IntegerField()),
                ('is_last_add', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CommentSentiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cid', models.IntegerField()),
                ('comment', models.TextField()),
                ('code', models.IntegerField()),
                ('message', models.CharField(max_length=200)),
                ('positive', models.DecimalField(max_digits=20, decimal_places=15)),
                ('negative', models.DecimalField(max_digits=20, decimal_places=15)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('p_url', models.CharField(max_length=200)),
                ('commenter', models.CharField(max_length=100)),
                ('c_url', models.CharField(max_length=100)),
                ('c_time', models.IntegerField()),
                ('star', models.IntegerField()),
                ('help', models.CharField(max_length=100)),
                ('comment', models.TextField()),
                ('hasImage', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='ProductNew',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('url', models.CharField(max_length=500)),
                ('price', models.CharField(max_length=20)),
                ('rank', models.IntegerField()),
                ('star', models.CharField(max_length=20)),
                ('commentPageNum', models.IntegerField()),
                ('comment_url', models.CharField(max_length=500)),
                ('is_last_add', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=100)),
                ('u_url', models.CharField(max_length=200)),
                ('p_name', models.CharField(max_length=100)),
                ('star', models.IntegerField()),
                ('suggestion', models.CharField(max_length=200)),
                ('help', models.CharField(max_length=100)),
                ('time', models.IntegerField()),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='UserNew',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_name', models.CharField(max_length=200)),
                ('rank', models.IntegerField()),
                ('help_receive', models.IntegerField()),
                ('help_useful', models.IntegerField()),
                ('pname', models.CharField(max_length=200)),
                ('pstar', models.CharField(max_length=20)),
                ('psuggestion', models.CharField(max_length=200)),
                ('pcomment', models.TextField()),
                ('is_last_add', models.IntegerField()),
            ],
        ),
    ]
