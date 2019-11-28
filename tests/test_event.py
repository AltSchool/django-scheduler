from __future__ import absolute_import
import datetime
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
import pytz
from dateutil import tz, relativedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from schedule.models import Event, Rule, Calendar, EventRelation


class TestEvent(TestCase):

    def setUp(self):
        cal = Calendar(name="MyCal")
        cal.save()

    def __create_event(self, title, start, end, cal):
        return Event(**{
                'title': title,
                'start': start,
                'end': end,
                'calendar': cal
               })

    def __create_recurring_event(self, title, start, end, end_recurring, rule, cal):
         return Event.objects.create(**{
                'title': title,
                'start': start,
                'end': end,
                'end_recurring_period': end_recurring,
                'rule': rule,
                'calendar': cal
               })


    def test_get_occurrences__years_old_events(self):
        """
        Test events across year-long boundaries. 
        TODO(faisal): Time to calculate events within start-end grows with the distance of start
        from the first event start. See how to optimize for that in the future
        """
        cal = Calendar(name="MyCal")
        cal.save()
        rule_weekly = Rule(frequency="WEEKLY")
        rule_weekly.save()

        # Rule that was defined previous year and occurrences are fetched for next year.
        event_params = {
            'title': 'Edge case event test one',
            'start': datetime.datetime(2014, 12, 29, 8, 0, tzinfo=pytz.utc),
            'end': datetime.datetime(2014, 12, 29, 8, 0, tzinfo=pytz.utc),
            'rule': rule_weekly
        }
        
        weekly_point_event = Event.objects.create(**event_params)
        occ1 = weekly_point_event.get_occurrences(datetime.datetime(2015, 1, 5, 8, 0, tzinfo=pytz.utc),
                                                datetime.datetime(2015, 2, 5, 8, 0, tzinfo=pytz.utc))
        self.assertEquals(5, len(occ1))

        # Rule that was defined several years ago and occurrences are fetched for a much later time
        event_params = {
            'title': 'Edge case event test one',
            'start': datetime.datetime(2009, 11, 0o2, 8, 0, tzinfo=pytz.utc),
            'end': datetime.datetime(2009, 11, 0o2, 8, 0, tzinfo=pytz.utc),
            'rule': rule_weekly
        }

        event = Event.objects.create(**event_params)
        occ2 = event.get_occurrences(datetime.datetime(2015, 1, 5, 8, 0, tzinfo=pytz.utc),
                                     datetime.datetime(2015, 2, 5, 8, 0, tzinfo=pytz.utc))

        self.assertEquals(5, len(occ2))
        
    #@profile
    def test_get_occurrences___cross_event_boundaries(self):
        """
        Event that was defined in the past that crosses day boundaries. The assumed behavior is that
        event occurrences that started before the given start parameter for get_occurrences() but
        finished after that parameter should be included. 

        eg. 
        Given: Event(rule='Daily', start="3/23/2015 10PM", end="3/24/2015 2AM")
        Compute: get_occurrences() between 3/30/2015 12AM and 3/31/2015 12AM
        Result: Should get 2 events, one fo th epar that overlaps the beginning of 3/30 and one that 
          overlaps the night/early morning for 3/30-3/31
        """
        rule_daily = Rule(frequency="DAILY")
        rule_daily.save()
        
        event_params = {
            'title': 'Daily event that crosses day boundaries',
            'start': datetime.datetime(2015, 3, 23, 22, 0, tzinfo=pytz.utc),
            'end': datetime.datetime(2015, 3, 24, 2, 0, tzinfo=pytz.utc),
            'rule': rule_daily
        }
        
        event = Event.objects.create(**event_params)
        occ1 = event.get_occurrences(datetime.datetime(2015, 3, 30, 0, 0, tzinfo=pytz.utc),
                                     datetime.datetime(2015, 4, 3, 23, 59, tzinfo=pytz.utc))

        self.assertEqual(6, len(occ1))
        self.assertEqual(datetime.datetime(2015, 3, 29, 22, 0, tzinfo=pytz.utc), occ1[0].start)
        self.assertEqual(datetime.datetime(2015, 3, 30, 2, 0, tzinfo=pytz.utc), occ1[0].end)

        self.assertEqual(datetime.datetime(2015, 4, 3, 22, 0, tzinfo=pytz.utc), occ1[-1].start)
        self.assertEqual(datetime.datetime(2015, 4, 4, 2, 0, tzinfo=pytz.utc), occ1[-1].end)

        event_params = {
            'title': 'Daily event that crosses day boundaries',
            'start': datetime.datetime(2015, 3, 23, 22, 0, tzinfo=pytz.utc),
            'end': datetime.datetime(2015, 3, 24, 2, 0, tzinfo=pytz.utc),
            'rule': rule_daily
        }
        event = Event.objects.create(**event_params)
        occ2 = event.get_occurrences(datetime.datetime(2015, 3, 31, 0, 0, tzinfo=pytz.utc),
                                     datetime.datetime(2015, 4, 1, 0, 0, tzinfo=pytz.utc))
        self.assertEqual(2, len(occ2))
        self.assertEqual(datetime.datetime(2015, 3, 30, 22, 0, tzinfo=pytz.utc), occ2[0].start)
        self.assertEqual(datetime.datetime(2015, 3, 31, 2, 0, tzinfo=pytz.utc), occ2[0].end)
        self.assertEqual(datetime.datetime(2015, 3, 31, 22, 0, tzinfo=pytz.utc), occ2[1].start)
        self.assertEqual(datetime.datetime(2015, 4, 1, 2, 0, tzinfo=pytz.utc), occ2[1].end)
        
        rule_weekly = Rule(frequency="WEEKLY")
        rule_weekly.save()
        event_params = {
            'title': 'Daily event that crosses day boundaries',
            'start': datetime.datetime(2015, 3, 23, 22, 0, tzinfo=pytz.utc),
            'end': datetime.datetime(2015, 3, 24, 2, 0, tzinfo=pytz.utc),
            'rule': rule_weekly
        }
        event = Event.objects.create(**event_params)
        occ3 = event.get_occurrences(datetime.datetime(2015, 3, 31, 0, 0, tzinfo=pytz.utc),
                                     datetime.datetime(2015, 4, 1, 0, 0, tzinfo=pytz.utc))
        self.assertEqual(1, len(occ3))
        self.assertEqual(datetime.datetime(2015, 3, 30, 22, 0, tzinfo=pytz.utc), occ3[0].start)
        self.assertEqual(datetime.datetime(2015, 3, 31, 2, 0, tzinfo=pytz.utc), occ3[0].end)

        

    def test_edge_case_events(self):
        cal = Calendar(name="MyCal")
        cal.save()
        data_1 = {
            'title': 'Edge case event test one',
            'start': datetime.datetime(2013, 1, 5, 8, 0, tzinfo=pytz.utc),
            'end': datetime.datetime(2013, 1, 5, 9, 0, tzinfo=pytz.utc),
            'calendar': cal
        }
        data_2 = {
            'title': 'Edge case event test two',
            'start': datetime.datetime(2013, 1, 5, 9, 0, tzinfo=pytz.utc),
            'end': datetime.datetime(2013, 1, 5, 12, 0, tzinfo=pytz.utc),
            'calendar': cal
        }
        event_one = Event(**data_1)
        event_two = Event(**data_2)
        event_one.save()
        event_two.save()
        occurrences_two = event_two.get_occurrences(datetime.datetime(2013, 1, 5, 9, 0, tzinfo=pytz.utc),
                                                    datetime.datetime(2013, 1, 5, 12, 0, tzinfo=pytz.utc))
        self.assertEquals(1, len(occurrences_two))

        occurrences_one = event_one.get_occurrences(datetime.datetime(2013, 1, 5, 9, 0, tzinfo=pytz.utc),
                                                    datetime.datetime(2013, 1, 5, 12, 0, tzinfo=pytz.utc))
        self.assertEquals(0, len(occurrences_one))

    def test_recurring_event_get_occurrences(self):
        recurring_event = Event(**self.recurring_data)
        occurrences = recurring_event.get_occurrences(start=datetime.datetime(2008, 1, 12, 0, 0, tzinfo=pytz.utc),
                                                      end=datetime.datetime(2008, 1, 20, 0, 0, tzinfo=pytz.utc))
        self.assertEquals(["%s to %s" % (o.start, o.end) for o in occurrences],
                          ['2008-01-12 08:00:00+00:00 to 2008-01-12 09:00:00+00:00',
                           '2008-01-19 08:00:00+00:00 to 2008-01-19 09:00:00+00:00'])

    def test_recurring_event_get_occurrences_dst(self):
        # PostgreSQL stores all datetimes in UTC, therefore we need to use a custom 
        # rule parameter to support forcing the timezone to a known target
        pacific_tz_name = "US/Pacific"

        pacific = tz.gettz(pacific_tz_name)
        utc = tz.gettz("UTC")

        calendar = Calendar.objects.create(name="test calender")
        rule = Rule.objects.get_or_create_by_frequency_and_timezone("WEEKLY", pacific_tz_name)

        before_dst = datetime.datetime(2015, 3, 4, 8, 0, 0, tzinfo=pacific) # 8am US/Pacific March 4th, 2015
        after_dst = before_dst + relativedelta.relativedelta(days=7)        # 8am US/Pacific March 11th, 2015

        # make sure astimezone works properly to convert between timezones
        self.assertEquals(datetime.datetime(2015, 3, 4, 16, 0, 0, tzinfo=utc), before_dst.astimezone(utc))

        # make sure relativedelta works properly across DST boundaries
        self.assertEquals(datetime.datetime(2015, 3, 11, 8, 0, 0, tzinfo=pacific), after_dst)
        self.assertEqual(datetime.datetime(2015, 3, 11, 15, 0, 0, tzinfo=utc), after_dst.astimezone(utc)) # note that the UTC offset has changed from -8 to -7

        recurring_event = self.__create_recurring_event(
          'Recurring event test get_occurrences over DST boundary',
          before_dst.astimezone(utc),
          before_dst.astimezone(utc),
          after_dst.astimezone(utc),
          rule,
          calendar)

        occurrences = recurring_event.get_occurrences(before_dst, after_dst)
        self.assertEquals([before_dst, after_dst], [o.start for o in occurrences])


        
    def test_event_get_occurrences_after(self):

        cal = Calendar(name="MyCal")
        cal.save()
        rule = Rule(frequency="WEEKLY")
        rule.save()

        recurring_event = self.__create_recurring_event(
                    'Recurrent event test get_occurrence',
                    datetime.datetime(2008, 1, 5, 8, 0, tzinfo=pytz.utc),
                    datetime.datetime(2008, 1, 5, 9, 0, tzinfo=pytz.utc),
                    datetime.datetime(2008, 5, 5, 0, 0, tzinfo=pytz.utc),
                    rule,
                    cal,
                    )
        event_one = self.__create_event(
                'Edge case event test one',
                datetime.datetime(2013, 1, 5, 8, 0, tzinfo=pytz.utc),
                datetime.datetime(2013, 1, 5, 9, 0, tzinfo=pytz.utc),
                cal
               )
        event_two = self.__create_event(
                'Edge case event test two',
                datetime.datetime(2013, 1, 5, 9, 0, tzinfo=pytz.utc),
                datetime.datetime(2013, 1, 5, 12, 0, tzinfo=pytz.utc),
                cal
               )
        event_one.save()
        event_two.save()
        occurrences_two = event_two.get_occurrences(
                                    datetime.datetime(2013, 1, 5, 9, 0, tzinfo=pytz.utc),
                                    datetime.datetime(2013, 1, 5, 12, 0, tzinfo=pytz.utc))

        self.assertEquals(1, len(occurrences_two))

        occurrences_one = event_one.get_occurrences(
                                    datetime.datetime(2013, 1, 5, 9, 0, tzinfo=pytz.utc),
                                    datetime.datetime(2013, 1, 5, 12, 0, tzinfo=pytz.utc))

        self.assertEquals(0, len(occurrences_one))

    def test_recurring_event_get_occurrences(self):
        cal = Calendar(name="MyCal")
        rule = Rule(frequency = "WEEKLY")
        rule.save()

        recurring_event = self.__create_recurring_event(
                                    'Recurring event test',
                                    datetime.datetime(2008, 1, 5, 8, 0, tzinfo=pytz.utc),
                                    datetime.datetime(2008, 1, 5, 9, 0, tzinfo=pytz.utc),
                                    datetime.datetime(2008, 5, 5, 0, 0, tzinfo=pytz.utc),
                                    rule,
                                    cal
                )
        occurrences = recurring_event.get_occurrences(
                                    start=datetime.datetime(2008, 1, 12, 0, 0, tzinfo=pytz.utc),
                                    end=datetime.datetime(2008, 1, 20, 0, 0, tzinfo=pytz.utc))

        self.assertEquals(["%s to %s" %(o.start, o.end) for o in occurrences],
                ['2008-01-12 08:00:00+00:00 to 2008-01-12 09:00:00+00:00', '2008-01-19 08:00:00+00:00 to 2008-01-19 09:00:00+00:00'])

    def test_recurring_event_get_occurrences_after(self):

        cal = Calendar(name="MyCal")
        cal.save()
        rule = Rule(frequency = "WEEKLY")
        rule.save()
        recurring_event= self.__create_recurring_event(
                    'Recurrent event test get_occurrence',
                    datetime.datetime(2008, 1, 5, 8, 0, tzinfo=pytz.utc),
                    datetime.datetime(2008, 1, 5, 9, 0, tzinfo=pytz.utc),
                    datetime.datetime(2008, 5, 5, 0, 0, tzinfo=pytz.utc),
                    rule,
                    cal,
                    )

        recurring_event.save()
        #occurrences = recurring_event.get_occurrences(start=datetime.datetime(2008, 1, 5, tzinfo=pytz.utc),
        #    end = datetime.datetime(2008, 1, 6, tzinfo=pytz.utc))
        #occurrence = occurrences[0]
        #occurrence2 = recurring_event.occurrences_after(datetime.datetime(2008, 1, 5, tzinfo=pytz.utc)).next()
        #self.assertEqual(occurrence, occurrence2)

        
    def test_recurring_event_get_occurrence(self):

        cal = Calendar(name="MyCal")
        cal.save()
        rule = Rule(frequency = "WEEKLY")
        rule.save()

        event = self.__create_recurring_event(
                    'Recurrent event test get_occurrence',
                    datetime.datetime(2008, 1, 5, 8, 0, tzinfo=pytz.utc),
                    datetime.datetime(2008, 1, 5, 9, 0, tzinfo=pytz.utc),
                    datetime.datetime(2008, 5, 5, 0, 0, tzinfo=pytz.utc),
                    rule,
                    cal,
                    )
        event.save()
        occurrence = event.get_occurrence(datetime.datetime(2008, 1, 5, 8, 0, tzinfo=pytz.utc))
        self.assertEqual(occurrence.start, datetime.datetime(2008, 1, 5, 8, tzinfo=pytz.utc))
        occurrence.save()
        occurrence = event.get_occurrence(datetime.datetime(2008, 1, 5, 8, 0, tzinfo=pytz.utc))
        self.assertTrue(occurrence.pk is not None)

    def test_prevent_type_error_when_comparing_naive_and_aware_dates(self):
        # this only test if the TypeError is raised
        cal = Calendar(name="MyCal")
        cal.save()
        rule = Rule(frequency = "WEEKLY")
        rule.save()

        event = self.__create_recurring_event(
                    'Recurrent event test get_occurrence',
                    datetime.datetime(2008, 1, 5, 8, 0, tzinfo=pytz.utc),
                    datetime.datetime(2008, 1, 5, 9, 0, tzinfo=pytz.utc),
                    datetime.datetime(2008, 5, 5, 0, 0, tzinfo=pytz.utc),
                    rule,
                    cal,
                    )
        naive_date = datetime.datetime(2008, 1, 20, 0, 0)
        self.assertIsNone(event.get_occurrence(naive_date))

    @override_settings(USE_TZ=False)
    def test_prevent_type_error_when_comparing_dates_when_tz_off(self):
        cal = Calendar(name="MyCal")
        cal.save()
        rule = Rule(frequency = "WEEKLY")
        rule.save()

        event = self.__create_recurring_event(
                    'Recurrent event test get_occurrence',
                    datetime.datetime(2008, 1, 5, 8, 0),
                    datetime.datetime(2008, 1, 5, 9, 0),
                    datetime.datetime(2008, 5, 5, 0, 0),
                    rule,
                    cal,
                    )
        naive_date = datetime.datetime(2008, 1, 20, 0, 0)
        self.assertIsNone(event.get_occurrence(naive_date))

    def test_event_get_ocurrence(self):

        cal = Calendar(name='MyCal')
        start = timezone.now() + datetime.timedelta(days=1)
        event = self.__create_event(
                            'Non recurring event test get_occurrence',
                            start,
                            start + datetime.timedelta(hours=1),
                            cal)


        occurrence = event.get_occurrence(start)
        self.assertEquals(occurrence.start, start)

    def test_occurences_after_with_no_params(self):

        cal = Calendar(name='MyCal')
        start = timezone.now() + datetime.timedelta(days=1)
        event = self.__create_event(
                            'Non recurring event test get_occurrence',
                            start,
                            start + datetime.timedelta(hours=1),
                            cal)

        occurrences = list(event.occurrences_after())
        self.assertEquals(len(occurrences), 1)
        self.assertEquals(occurrences[0].start, start)
        self.assertEquals(occurrences[0].end, start + datetime.timedelta(hours=1))


    def test_occurences_with_recurrent_event_end_recurring_period_edge_case(self):

        cal = Calendar(name='MyCal')

        rule = Rule(frequency = "DAILY")
        rule.save()
        start = timezone.now() + datetime.timedelta(days=1)
        event = self.__create_recurring_event(
                            'Non recurring event test get_occurrence',
                            start,
                            start + datetime.timedelta(hours=1),
                            start + datetime.timedelta(days=10),
                            rule,
                            cal)
        occurrences = list(event.occurrences_after())
        self.assertEquals(len(occurrences), 11)

    def test_get_for_object(self):
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        event_relations = list(Event.objects.get_for_object(user, 'owner', inherit=False))
        self.assertEquals(len(event_relations), 0)

        rule = Rule(frequency = "DAILY")
        rule.save()
        cal = Calendar(name='MyCal')
        cal.save()
        event = self.__create_event(
                'event test',
                datetime.datetime(2013, 1, 5, 8, 0, tzinfo=pytz.utc),
                datetime.datetime(2013, 1, 5, 9, 0, tzinfo=pytz.utc),
                cal
               )
        event.save()
        events = list(Event.objects.get_for_object(user, 'owner', inherit=False))
        self.assertEquals(len(events), 0)
        EventRelation.objects.create_relation(event, user, 'owner')

        events = list(Event.objects.get_for_object(user, 'owner', inherit=False))
        self.assertEquals(len(events), 1)
        self.assertEquals(event, events[0])

    def test_get_absolute(self):
        cal = Calendar(name='MyCal')
        cal.save()
        rule = Rule(frequency = "DAILY")
        rule.save()
        start = timezone.now() + datetime.timedelta(days=1)
        event = self.__create_recurring_event(
                            'Non recurring event test get_occurrence',
                            start,
                            start + datetime.timedelta(hours=1),
                            start + datetime.timedelta(days=10),
                            rule,
                            cal)
        event.save()
        url = event.get_absolute_url()
        self.assertEquals(reverse('event', kwargs={'event_id': event.id}), url)

    def test_(self):
        pass

class TestEventRelationManager(TestCase):

    def test_get_events_for_object(self):
        pass
