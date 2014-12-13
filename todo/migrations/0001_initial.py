# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ToDo',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('item', models.TextField(default='')),
                ('added_by', models.IntegerField()),
                ('date_todo', models.DateTimeField()),
                ('archive', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
