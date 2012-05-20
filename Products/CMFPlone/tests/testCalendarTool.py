from DateTime import DateTime
from Products.CMFPlone.tests import PloneTestCase


class TestCalendarTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.calendar = self.portal.portal_calendar
        self.calendar.firstweekday = 0
        self.workflow = self.portal.portal_workflow
        self.event_date = DateTime('2008-02-08 0:00:00')
        self.populateSite()

    def populateSite(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Event', 'event1')
        event1 = getattr(self.portal, 'event1')
        event1.edit(startDate=self.event_date, endDate=self.event_date)
        self.workflow.doActionFor(event1, 'publish', comment='testing')
        self.portal.invokeFactory('Folder', 'folder1')
        folder1 = getattr(self.portal, 'folder1')
        folder1.invokeFactory('Event', 'event11')
        event11 = getattr(self.portal.folder1, 'event11')
        event11.edit(startDate=self.event_date, endDate=self.event_date)
        self.workflow.doActionFor(event11, 'publish', comment='testing')
        self.setRoles(['Member'])

    def testGetEventsForCalendar(self):
        events = self.calendar.getEventsForCalendar(
                                  month=self.event_date.month(),
                                  year=self.event_date.year())

        data = [
         [{'eventslist': [], 'day': 0, 'event': 0},
          {'eventslist': [], 'day': 0, 'event': 0},
          {'eventslist': [], 'day': 0, 'event': 0},
          {'eventslist': [], 'day': 0, 'event': 0},
          {'eventslist': [], 'day': 1, 'event': 0},
          {'eventslist': [], 'day': 2, 'event': 0},
          {'eventslist': [], 'day': 3, 'event': 0}],
         [{'eventslist': [], 'day': 4, 'event': 0},
          {'eventslist': [], 'day': 5, 'event': 0},
          {'eventslist': [], 'day': 6, 'event': 0},
          {'eventslist': [], 'day': 7, 'event': 0},
          {'day': 8,
           'event': 1,
           'eventslist': [{'end': '00:00:00',
                           'start': '00:00:00',
                           'title': 'event1'},
                          {'end': '00:00:00',
                           'start': '00:00:00',
                           'title': 'event11'}]},
          {'eventslist': [], 'day': 9, 'event': 0},
          {'eventslist': [], 'day': 10, 'event': 0}],
         [{'eventslist': [], 'day': 11, 'event': 0},
          {'eventslist': [], 'day': 12, 'event': 0},
          {'eventslist': [], 'day': 13, 'event': 0},
          {'eventslist': [], 'day': 14, 'event': 0},
          {'eventslist': [], 'day': 15, 'event': 0},
          {'eventslist': [], 'day': 16, 'event': 0},
          {'eventslist': [], 'day': 17, 'event': 0}],
         [{'eventslist': [], 'day': 18, 'event': 0},
          {'eventslist': [], 'day': 19, 'event': 0},
          {'eventslist': [], 'day': 20, 'event': 0},
          {'eventslist': [], 'day': 21, 'event': 0},
          {'eventslist': [], 'day': 22, 'event': 0},
          {'eventslist': [], 'day': 23, 'event': 0},
          {'eventslist': [], 'day': 24, 'event': 0}],
         [{'eventslist': [], 'day': 25, 'event': 0},
          {'eventslist': [], 'day': 26, 'event': 0},
          {'eventslist': [], 'day': 27, 'event': 0},
          {'eventslist': [], 'day': 28, 'event': 0},
          {'eventslist': [], 'day': 29, 'event': 0},
          {'eventslist': [], 'day': 0, 'event': 0},
          {'eventslist': [], 'day': 0, 'event': 0}]]

        self.assertEqual(events, data)

    def testGetEventsForCalendarInPath(self):
        path = "/".join(self.portal.folder1.getPhysicalPath())
        events = self.calendar.getEventsForCalendar(
                    month=self.event_date.month(),
                    year=self.event_date.year(),
                    path=path)
        data = [
         [{'eventslist': [], 'day': 0, 'event': 0},
          {'eventslist': [], 'day': 0, 'event': 0},
          {'eventslist': [], 'day': 0, 'event': 0},
          {'eventslist': [], 'day': 0, 'event': 0},
          {'eventslist': [], 'day': 1, 'event': 0},
          {'eventslist': [], 'day': 2, 'event': 0},
          {'eventslist': [], 'day': 3, 'event': 0}],
         [{'eventslist': [], 'day': 4, 'event': 0},
          {'eventslist': [], 'day': 5, 'event': 0},
          {'eventslist': [], 'day': 6, 'event': 0},
          {'eventslist': [], 'day': 7, 'event': 0},
          {'day': 8,
           'event': 1,
           'eventslist': [{'end': '00:00:00',
                           'start': '00:00:00',
                           'title': 'event11'}]},
          {'eventslist': [], 'day': 9, 'event': 0},
          {'eventslist': [], 'day': 10, 'event': 0}],
         [{'eventslist': [], 'day': 11, 'event': 0},
          {'eventslist': [], 'day': 12, 'event': 0},
          {'eventslist': [], 'day': 13, 'event': 0},
          {'eventslist': [], 'day': 14, 'event': 0},
          {'eventslist': [], 'day': 15, 'event': 0},
          {'eventslist': [], 'day': 16, 'event': 0},
          {'eventslist': [], 'day': 17, 'event': 0}],
         [{'eventslist': [], 'day': 18, 'event': 0},
          {'eventslist': [], 'day': 19, 'event': 0},
          {'eventslist': [], 'day': 20, 'event': 0},
          {'eventslist': [], 'day': 21, 'event': 0},
          {'eventslist': [], 'day': 22, 'event': 0},
          {'eventslist': [], 'day': 23, 'event': 0},
          {'eventslist': [], 'day': 24, 'event': 0}],
         [{'eventslist': [], 'day': 25, 'event': 0},
          {'eventslist': [], 'day': 26, 'event': 0},
          {'eventslist': [], 'day': 27, 'event': 0},
          {'eventslist': [], 'day': 28, 'event': 0},
          {'eventslist': [], 'day': 29, 'event': 0},
          {'eventslist': [], 'day': 0, 'event': 0},
          {'eventslist': [], 'day': 0, 'event': 0}]]

        self.assertEqual(events, data)

    def testCatalogGetEvents(self):
        events = self.calendar.catalog_getevents(
                    month=self.event_date.month(),
                    year=self.event_date.year())
        data = [
         {'eventslist': [], 'day': 2, 'event': 0},
         {'eventslist': [], 'day': 3, 'event': 0},
         {'eventslist': [], 'day': 4, 'event': 0},
         {'eventslist': [], 'day': 5, 'event': 0},
         {'eventslist': [], 'day': 6, 'event': 0},
         {'eventslist': [], 'day': 7, 'event': 0},
         {'day': 8,
          'event': 1,
          'eventslist': [{'start': '00:00:00',
                          'end': '00:00:00',
                          'title': 'event1'},
                         {'end': '00:00:00',
                          'start': '00:00:00',
                          'title': 'event11'}]}]

        self.assertEqual([events[e] for e in range(2, 9)], data)

    def testCatalogGetEventsInPath(self):
        path = "/".join(self.portal.folder1.getPhysicalPath())
        events = self.calendar.catalog_getevents(
                    month=self.event_date.month(),
                    year=self.event_date.year(),
                    path=path)
        data = [
         {'eventslist': [], 'day': 2, 'event': 0},
         {'eventslist': [], 'day': 3, 'event': 0},
         {'eventslist': [], 'day': 4, 'event': 0},
         {'eventslist': [], 'day': 5, 'event': 0},
         {'eventslist': [], 'day': 6, 'event': 0},
         {'eventslist': [], 'day': 7, 'event': 0},
         {'day': 8,
          'event': 1,
          'eventslist': [{'end': '00:00:00',
                          'start': '00:00:00',
                          'title': 'event11'}]}]

        self.assertEqual([events[e] for e in range(2, 9)], data)
