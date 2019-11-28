from __future__ import absolute_import
from django.contrib import admin

from schedule.models import Calendar, Event, CalendarRelation, Rule

class CalendarAdminOptions(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']


admin.site.register(Calendar, CalendarAdminOptions)
admin.site.register([Rule, Event, CalendarRelation])
