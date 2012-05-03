from StringIO import StringIO
from time import localtime

from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider

from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.component import getMultiAdapter

from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PythonScripts.standard import url_quote_plus

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets import cache
from plone.app.portlets.portlets import base

PLMF = MessageFactory('plonelocales')


class ICalendarPortlet(IPortletDataProvider):
    """A portlet displaying a calendar
    """


class Assignment(base.Assignment):
    implements(ICalendarPortlet)

    title = _(u'Calendar')


def _render_cachekey(fun, self):
    context = aq_inner(self.context)
    if not self.updated:
        self.update()

    if self.calendar.getUseSession():
        raise ram.DontCache()
    else:
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        key = StringIO()
        print >> key, portal_state.navigation_root_url()
        print >> key, cache.get_language(context, self.request)
        print >> key, self.calendar.getFirstWeekDay()

        year, month = self.getYearAndMonthToDisplay()
        print >> key, year
        print >> key, month

        navigation_root_path = portal_state.navigation_root_path()
        start = DateTime('%s/%s/1' % (year, month))
        end = DateTime('%s/%s/1 23:59:59' % self.getNextMonth(year, month)) - 1

        def add(brain):
            key.write(brain.getPath())
            key.write('\n')
            key.write(brain.modified)
            key.write('\n\n')

        catalog = getToolByName(context, 'portal_catalog')
        path = navigation_root_path
        brains = catalog(
            portal_type=self.calendar.getCalendarTypes(),
            review_state=self.calendar.getCalendarStates(),
            start={'query': end, 'range': 'max'},
            end={'query': start, 'range': 'min'},
            path=path)

        for brain in brains:
            add(brain)

        return key.getvalue()


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('calendar.pt')
    updated = False

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.updated = False

    def update(self):
        if self.updated:
            return
        self.updated = True

        context = aq_inner(self.context)
        self.calendar = getToolByName(context, 'portal_calendar')
        self._ts = getToolByName(context, 'translation_service')
        self.url_quote_plus = url_quote_plus

        self.now = localtime()
        self.yearmonth = yearmonth = self.getYearAndMonthToDisplay()
        self.year = year = yearmonth[0]
        self.month = month = yearmonth[1]

        self.showPrevMonth = yearmonth > (self.now[0]-1, self.now[1])
        self.showNextMonth = yearmonth < (self.now[0]+1, self.now[1])

        self.prevMonthYear, self.prevMonthMonth = self.getPreviousMonth(year, month)
        self.nextMonthYear, self.nextMonthMonth = self.getNextMonth(year, month)

        self.monthName = PLMF(self._ts.month_msgid(month),
                              default=self._ts.month_english(month))

    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    def getEventsForCalendar(self):
        context = aq_inner(self.context)
        year = self.year
        month = self.month
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()
        weeks = self.calendar.getEventsForCalendar(month, year, path=navigation_root_path)
        for week in weeks:
            for day in week:
                daynumber = day['day']
                if daynumber == 0:
                    continue
                day['is_today'] = self.isToday(daynumber)
                if day['event']:
                    cur_date = DateTime(year, month, daynumber)
                    localized_date = [self._ts.ulocalized_time(cur_date, context=context, request=self.request)]
                    day['eventstring'] = '\n'.join(localized_date+[' %s' %
                        self.getEventString(e) for e in day['eventslist']])
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
            year = self.now[0]
        if not month:
            month = self.now[1]

        # try to transform to number but fall back to current
        # date if this is ambiguous
        try:
            year, month = int(year), int(month)
        except (TypeError, ValueError):
            year, month = self.now[:2]

        # Store the results in the session for next time
        if session:
            session.set('calendar_year', year)
            session.set('calendar_month', month)

        # Finally return the results
        return year, month

    def getPreviousMonth(self, year, month):
        if month==0 or month==1:
            month, year = 12, year - 1
        else:
            month-=1
        return (year, month)

    def getNextMonth(self, year, month):
        if month==12:
            month, year = 1, year + 1
        else:
            month+=1
        return (year, month)

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
        return self.now[2]==day and self.now[1]==self.month and \
               self.now[0]==self.year

    def getReviewStateString(self):
        states = self.calendar.getCalendarStates()
        return ''.join(map(lambda x: 'review_state=%s&amp;' % self.url_quote_plus(x), states))

    def getQueryString(self):
        request = self.request
        query_string = request.get('orig_query',
                                   request.get('QUERY_STRING', None))
        if len(query_string) == 0:
            query_string = ''
        else:
            query_string = '%s&amp;' % query_string
        return query_string


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
