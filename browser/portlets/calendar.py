from DateTime import DateTime
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import ICalendarPortlet


class CalendarPortlet(utils.BrowserView):
    implements(ICalendarPortlet)

    def __init__(self, context, request):
        self.context = [context]
        self.request = request
        self.yearmonth = self.getYearAndMonthToDisplay()
        self.DateTime = DateTime
        self.current = DateTime()
        self.current_day = self.current.day()
        self.nextYearMax = self.current + 365
        self.prevYearMin = self.current - 365
        self.year = self.yearmonth[0]
        self.month = self.yearmonth[1]
        self.prevMonthTime = self.getPreviousMonth(self.month, self.year)
        self.nextMonthTime = self.getNextMonth(self.month, self.year)
        calendar = getToolByName(context, 'portal_calendar')
        self.weeks = calendar.getEventsForCalendar(self.month, self.year)

    def getYearAndMonthToDisplay(self):
        """ from skins/plone_scripts/getYearAndMonthToDisplay.py """

        current = DateTime()
        context = utils.context(self)
        request = self.request
        session = None

        # First priority goes to the data in the REQUEST
        year = request.get('year', None)
        month = request.get('month', None)

        # Next get the data from the SESSION
        if context.portal_calendar.getUseSession():  # XXX GoldEgg changed from 'container' to 'context'
            session = request.get('SESSION', None)
            if session:
                if not year:
                    year = session.get('calendar_year', None)
                if not month:
                    month = session.get('calendar_month', None)

        # Last resort to today
        if not year:
            year = current.year()
        if not month:
            month = current.month()

        year, month = int(year), int(month)

        # Store the results in the session for next time
        if session:
            session.set('calendar_year', year)
            session.set('calendar_month', month)

        # Finally return the results
        return year, month

    def getPreviousMonth(self, month, year):

        month=int(month)
        year=int(year)

        if month==0 or month==1:
            month, year = 12, year - 1
        else:
            month-=1

        return DateTime(year, month, 1)

    def getNextMonth(self, month, year):

        month=int(month)
        year=int(year)

        if month==12:
            month, year = 1, year + 1
        else:
            month+=1

        return DateTime(year, month, 1)
