# Tests the CalendarPortlet View
#

from Products.CMFPlone.tests import PloneTestCase

from Products.CMFPlone.tests.PloneTestCase import default_user
from Products.CMFPlone.tests.PloneTestCase import default_password

from DateTime import DateTime

from Products.ATContentTypes.tests.utils import FakeRequestSession

# BBB Plone 4.0
import warnings
showwarning = warnings.showwarning
warnings.showwarning = lambda *a, **k: None
# ignore deprecation warnings on import
from Products.CMFPlone.browser.interfaces import ICalendarPortlet
from Products.CMFPlone.browser.portlets.calendar import CalendarPortlet
# restore warning machinery
warnings.showwarning = showwarning


class TestCalendarPortletView(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.url = self.portal.portal_url
        self.calendar = self.portal.portal_calendar
        self.now = DateTime()

    def testImplementsICalendarPortlet(self):
        """CalendarPortlet must implement ICalendarPortlet"""
        self.failUnless(ICalendarPortlet.implementedBy(CalendarPortlet))

    def testGetYearAndMonthToDisplay(self):
        """CalendarPortlet.getYearAndMonthToDisplay() must return the current
           year and month.
        """
        view = CalendarPortlet(self.portal, self.app.REQUEST)
        result = view.getYearAndMonthToDisplay()
        self.failUnlessEqual(result, (self.now.year(), self.now.month()))
        
    def testGetYearAndMonthToDisplayRequest(self):
        """CalendarPortlet.getYearAndMonthToDisplay() must return the year and
           month found in REQUEST variables.
        """
        self.app.REQUEST['year'] = 2005
        self.app.REQUEST['month'] = 7
        view = CalendarPortlet(self.portal, self.app.REQUEST)
        result = view.getYearAndMonthToDisplay()
        self.failUnlessEqual(result, (2005, 7))

    def testGetYearAndMonthToDisplaySession(self):
        """CalendarPortlet.getYearAndMonthToDisplay() must return the year and
           month found in SESSION variables if this is enables in the calendar
           tool.
        """
        usesession = self.calendar.getUseSession()
        self.app.REQUEST['SESSION'] = FakeRequestSession()
        self.app.REQUEST['SESSION']['calendar_year'] = 2004
        self.app.REQUEST['SESSION']['calendar_month'] = 6
        
        # Ignore the session variables and use the current date
        self.calendar.use_session = False
        view = CalendarPortlet(self.portal, self.app.REQUEST)
        result = view.getYearAndMonthToDisplay()
        self.failUnlessEqual(result, (self.now.year(), self.now.month()))
        
        # Use the session variables
        self.calendar.use_session = True
        view = CalendarPortlet(self.portal, self.app.REQUEST)
        result = view.getYearAndMonthToDisplay()
        self.failUnlessEqual(result, (2004, 6))
        
        # Restore the orginal value
        self.calendar.use_session = usesession

    def testGetPreviousMonth(self):
        view = CalendarPortlet(self.portal, self.app.REQUEST)
        result = view.getPreviousMonth(12, 2006)
        self.failUnlessEqual(result, DateTime(2006, 11, 1))
        
        result = view.getPreviousMonth(1, 2006)
        self.failUnlessEqual(result, DateTime(2005, 12, 1))

    def testGetNextMonth(self):
        view = CalendarPortlet(self.portal, self.app.REQUEST)
        result = view.getNextMonth(12, 2006)
        self.failUnlessEqual(result, DateTime(2007, 1, 1))
        
        result = view.getNextMonth(1, 2006)
        self.failUnlessEqual(result, DateTime(2006, 2, 1))

    def testIsToday(self):
        view = CalendarPortlet(self.portal, self.app.REQUEST)
        self.failUnless(view.isToday(self.now.day()))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCalendarPortletView))
    return suite
