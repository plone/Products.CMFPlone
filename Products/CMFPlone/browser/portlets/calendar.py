from Acquisition import aq_inner
import zope.deprecation
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from DateTime import DateTime
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.interfaces import ICalendarPortlet

PLMF = MessageFactory('plonelocales')

class CalendarPortlet(BrowserView):
    implements(ICalendarPortlet)

    def __init__(self, context, request):
        self.context = context
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
        self.daynumbers = calendar.getDayNumbers()
        self._translation_service = getToolByName(context, 'translation_service')
        self.showStates = calendar.getCalendarStates()
        self.showPrevMonth = self.yearmonth > (self.prevYearMin.year(), self.prevYearMin.month())
        self.showNextMonth = self.yearmonth < (self.nextYearMax.year(), self.nextYearMax.month())

    def getYearAndMonthToDisplay(self):
        """ from skins/plone_scripts/getYearAndMonthToDisplay.py """

        current = DateTime()
        context = aq_inner(self.context)
        request = self.request
        session = None

        # First priority goes to the data in the REQUEST
        year = request.get('year', None)
        month = request.get('month', None)

        # Next get the data from the SESSION
        if context.portal_calendar.getUseSession():
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

    def getWeekdays(self):
        """Returns a list of Messages for the weekday names."""

        weekdays = []
        # list of ordered weekdays as numbers
        for day in self.daynumbers:
            msgid   = self._translation_service.day_msgid(day, format='s')
            english = self._translation_service.weekday_english(day, format='a')
            weekdays.append(PLMF(msgid, default=english))

        return weekdays

    def getEnglishMonthName(self):
        """Returns the current English month name."""
        return self._translation_service.month_english(self.month)

    def getMonthName(self):
        """Returns the current month name as a Message."""
        msgid   = self._translation_service.month_msgid(self.month)
        english = self._translation_service.month_english(self.month)
        return PLMF(msgid, default=english)

    def isToday(self, day):
        """Returns True if the given day and the current month and year equals
           today, otherwise False.
        """
        return self.current_day==day and self.current.month()==self.month and \
               self.current.year()==self.year

zope.deprecation.deprecated(
  ('CalendarPortlet', ),
   "Plone's portlets are based on plone.app.portlets now. The old portlets "
   "will be removed in Plone 4.0."
  )
