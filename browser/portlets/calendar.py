
from Products.CMFPlone.browser.interfaces import ICalendarPortlet

from zope.interface import implements
from zope.component import getView
from Products.Five import BrowserView
from DateTime import DateTime

class CalendarPortlet(BrowserView):
    implements(ICalendarPortlet)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.current = self.DateTime()()
        self.yearmonth = self.getYearAndMonthToDisplay()

    def DateTime(self):
        return DateTime

    def current(self):
        return self.current

    def current_day(self):
        return self.current.day()

    def nextYearMax(self):
        return self.current + 365

    def prevYearMin(self):
        return self.current - 365

    def year(self):
        return self.yearmonth[0]

    def month(self):
        return self.yearmonth[1]

    def prevMonthTime(self):
        return self.getPreviousMonth(self.month(), self.year())

    def nextMonthTime(self):
        return self.getNextMonth(self.month(), self.year())

    def weeks(self):
        return self.context.portal_calendar.getEventsForCalendar(self.month(), self.year())

    def getYearAndMonthToDisplay(self):
        """ from skins/plone_scripts/getYearAndMonthToDisplay.py """

        ##parameters=
        ##title=Calendar Presentation Helper

        # Returns the year and month that the calendar portlet should display.
        # If uses_session is true stores the values in the session.

        current = DateTime()
        request = self.request
        session = None

        # First priority goes to the data in the REQUEST
        year = request.get('year', None)
        month = request.get('month', None)

        # Next get the data from the SESSION
        if self.context.portal_calendar.getUseSession():  # XXX GoldEgg changed from 'container' to 'context'
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
        """ from skins/plone_scripts/getYearAndMonthToDisplay.py """
        ## Script (Python) "getPreviousMonth"
        ##bind container=container
        ##bind context=context
        ##bind namespace=
        ##bind script=script
        ##bind subpath=traverse_subpath
        ##parameters=month, year
        ##title=Calendar Presentation Helper
        ##

        month=int(month)
        year=int(year)

        if month==0 or month==1:
            month, year = 12, year - 1
        else:
            month-=1

        return DateTime(year, month, 1)

    def getNextMonth(self, month, year):
        """ from skins/plone_scripts/getYearAndMonthToDisplay.py """
        ## Script (Python) "getNextMonth"
        ##bind container=container
        ##bind context=context
        ##bind namespace=
        ##bind script=script
        ##bind subpath=traverse_subpath
        ##parameters=month, year
        ##title=Calendar Presentation Helper
        ##

        month=int(month)
        year=int(year)

        if month==12:
            month, year = 1, year + 1
        else:
            month+=1

        return DateTime(year, month, 1)

