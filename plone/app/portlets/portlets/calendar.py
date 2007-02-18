from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PythonScripts.standard import url_quote_plus

PLMF = MessageFactory('plonelocales')

class ICalendarPortlet(IPortletDataProvider):
    """A portlet displaying a calendar
    """

class Assignment(base.Assignment):
    implements(ICalendarPortlet)

    title = _(u'Calendar')

class Renderer(base.Renderer):

    render = ViewPageTemplateFile('calendar.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

        self.calendar = getToolByName(context, 'portal_calendar')
        self._ts = getToolByName(context, 'translation_service')
        self.url_quote_plus = url_quote_plus

        self.current = DateTime()
        self.current_day = self.current.day()

        self.yearmonth = self.getYearAndMonthToDisplay()
        self.year = self.yearmonth[0]
        self.month = self.yearmonth[1]

        nextYearMax = self.current + 365
        prevYearMin = self.current - 365
        self.showPrevMonth = self.yearmonth > (prevYearMin.year(), prevYearMin.month())
        self.showNextMonth = self.yearmonth < (nextYearMax.year(), nextYearMax.month())

        self.prevMonthTime = self.getPreviousMonth(self.month, self.year)
        self.nextMonthTime = self.getNextMonth(self.month, self.year)

        self.monthName = PLMF(self._ts.month_msgid(self.month),
                              default=self._ts.month_english(self.month))

        states = self.calendar.getCalendarStates()
        self.review_state_string = self.getReviewStateString(states)
        self.weeks = self.getEventsForCalendar(self.month, self.year)

    def getEventsForCalendar(self, month, year):
        weeks = self.calendar.getEventsForCalendar(month, year)
        for week in weeks:
            for day in week:
                daynumber = day['day']
                if daynumber == 0:
                    continue
                day['is_today'] = self.isToday(daynumber)
                if day['event']:
                    cur_date = DateTime(year, month, daynumber)
                    localized_date = [self._ts.ulocalized_time(cur_date, self.context)]
                    day['eventstring'] = '\n'.join(localized_date+[self.getEventString(e) for e in day['eventslist']])
                    day['date_string'] = '%s-%s-%s' % (year, month, daynumber)

        return weeks

    def getEventString(self, event):
        start = event['start'] and ':'.join(event['start'].split(':')[:2]) or ''
        end = event['end'] and ':'.join(event['end'].split(':')[:2]) or ''
        title = safe_unicode(event['title']) or u'event'

        if start and end:
            eventstring = "%s-%s %s" % (start, end, title)
        elif start: # can assume not event['end']
            eventstring = "%s - %s" % (start, title)
        elif event['end']: # can assume not event['start']
            eventstring = "%s - %s" % (title, end)
        else: # can assume not event['start'] and not event['end']
            eventstring = title

        return eventstring

    def getYearAndMonthToDisplay(self):
        session = None
        request = self.request

        # First priority goes to the data in the REQUEST
        year = request.get('year', None)
        month = request.get('month', None)

        # Next get the data from the SESSION
        if self.calendar.getUseSession():
            session = request.get('SESSION', None)
            if session:
                if not year:
                    year = session.get('calendar_year', None)
                if not month:
                    month = session.get('calendar_month', None)

        # Last resort to today
        if not year:
            year = self.current.year()
        if not month:
            month = self.current.month()

        year, month = int(year), int(month)

        # Store the results in the session for next time
        if session:
            session.set('calendar_year', year)
            session.set('calendar_month', month)

        # Finally return the results
        return year, month

    @memoize
    def getPreviousMonth(self, month, year):
        month=int(month)
        year=int(year)

        if month==0 or month==1:
            month, year = 12, year - 1
        else:
            month-=1
        return DateTime(year, month, 1)

    @memoize
    def getNextMonth(self, month, year):
        month=int(month)
        year=int(year)

        if month==12:
            month, year = 1, year + 1
        else:
            month+=1
        return DateTime(year, month, 1)

    def getWeekdays(self):
        """Returns a list of Messages for the weekday names."""
        weekdays = []
        # list of ordered weekdays as numbers
        for day in self.calendar.getDayNumbers():
            weekdays.append(PLMF(self._ts.day_msgid(day, format='s'),
                                 default=self._ts.weekday_english(day, format='a')))

        return weekdays

    def isToday(self, day):
        """Returns True if the given day and the current month and year equals
           today, otherwise False.
        """
        return self.current_day==day and self.current.month()==self.month and \
               self.current.year()==self.year

    @memoize
    def getReviewStateString(self, showStates):
        return ''.join(map(lambda x : 'review_state=%s&amp;' % self.url_quote_plus(x), showStates))


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
