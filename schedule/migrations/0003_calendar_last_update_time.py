# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_event_recent_start'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendar',
            name='last_update_time',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
            preserve_default=True,
        ),
    ]
