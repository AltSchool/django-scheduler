from __future__ import absolute_import
from django.conf.urls import url
from django.views.generic.list import ListView
from schedule.models import Calendar
from schedule.feeds import UpcomingEventsFeed
from schedule.feeds import CalendarICalendar
from schedule.periods import Year, Month, Week, Day
from schedule.views import (
    api_occurrences,
    DeleteEventView,
    event,
    calendar,
    calendar_by_periods,
    create_or_edit_event,
    occurrence,
    cancel_occurrence,
    edit_occurrence,
)

urlpatterns = [
    # urls for Calendars
    # Hack of just getting the most recent calendars.
    url(r'^calendar/$',
        ListView.as_view(queryset=Calendar.objects.all().filter(id__gt=1550).order_by('name'),
                         template_name='schedule/calendar_list.html'),
        name="calendar_list"),

    url(r'^calendar/year/(?P<calendar_slug>[-\w]+)/$',
        calendar_by_periods,
        name="year_calendar",
        kwargs={'periods': [Year], 'template_name': 'schedule/calendar_year.html'}),

    url(r'^calendar/tri_month/(?P<calendar_slug>[-\w]+)/$',
        calendar_by_periods,
        name="tri_month_calendar",
        kwargs={'periods': [Month], 'template_name': 'schedule/calendar_tri_month.html'}),

    url(r'^calendar/compact_month/(?P<calendar_slug>[-\w]+)/$',
        calendar_by_periods,
        name="compact_calendar",
        kwargs={'periods': [Month], 'template_name': 'schedule/calendar_compact_month.html'}),

    url(r'^calendar/month/(?P<calendar_slug>[-\w]+)/$',
        calendar_by_periods,
        name="month_calendar",
        kwargs={'periods': [Month], 'template_name': 'schedule/calendar_month.html'}),

    url(r'^calendar/week/(?P<calendar_slug>[-\w]+)/$',
        calendar_by_periods,
        name="week_calendar",
        kwargs={'periods': [Week], 'template_name': 'schedule/calendar_week.html'}),

    url(r'^calendar/daily/(?P<calendar_slug>[-\w]+)/$',
        calendar_by_periods,
        name="day_calendar",
        kwargs={'periods': [Day], 'template_name': 'schedule/calendar_day.html'}),

    url(r'^calendar/(?P<calendar_slug>[-\w]+)/$',
        calendar,
        name="calendar_home",
        ),

    # Event Urls
    url(r'^event/create/(?P<calendar_slug>[-\w]+)/$',
        create_or_edit_event,
        name='calendar_create_event'),
    url(r'^event/edit/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$',
        create_or_edit_event,
        name='edit_event'),
    url(r'^event/(?P<event_id>\d+)/$',
        event,
        name="event"),
    url(r'^event/delete/(?P<event_id>\d+)/$',
        DeleteEventView.as_view(),
        name="delete_event"),

    # urls for already persisted occurrences
    url(r'^occurrence/(?P<event_id>\d+)/(?P<occurrence_id>\d+)/$',
        occurrence,
        name="occurrence"),
    url(r'^occurrence/cancel/(?P<event_id>\d+)/(?P<occurrence_id>\d+)/$',
        cancel_occurrence,
        name="cancel_occurrence"),
    url(r'^occurrence/edit/(?P<event_id>\d+)/(?P<occurrence_id>\d+)/$',
        edit_occurrence,
        name="edit_occurrence"),

    #urls for unpersisted occurrences
    url(r'^occurrence/(?P<event_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$',
        occurrence,
        name="occurrence_by_date"),
    url(r'^occurrence/cancel/(?P<event_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$',
        cancel_occurrence,
        name="cancel_occurrence_by_date"),
    url(r'^occurrence/edit/(?P<event_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$',
        edit_occurrence,
        name="edit_occurrence_by_date"),

    #feed urls
    url(r'^feed/calendar/upcoming/(.*)/$',
        UpcomingEventsFeed(),
        name='upcoming_events_feed'),
    url(r'^ical/calendar/(.*)/$',
        CalendarICalendar(),
        name='calendar_ical'),
    #api urls
    url(r'^api/occurrences',
        api_occurrences,
        name='api_occurences'),

    url(r'^$',
        ListView.as_view(queryset=Calendar.objects.all()),
        name='schedule'),
]
