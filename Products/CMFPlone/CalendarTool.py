from Products.CMFCalendar.CalendarTool import CalendarTool as BaseTool
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from plone.event.interfaces import IRecurrenceSupport


class CalendarTool(PloneBaseTool, BaseTool):

    meta_type = 'Plone Calendar Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/event_icon.png'

    firstweekday = 0 # 0 is Monday

    security.declarePublic('getDayNumbers')
    def getDayNumbers(self):
        """ Returns a list of daynumbers with the correct start day first.

        >>> import calendar

        CMFCalendar / Python's calendar module and the translation service tool
        use different values for the first day of week. To get the right
        localized day names with the translation service tool we need a method
        to return the days in the order used by CMFCalendar.

        >>> fwday = (calendar.firstweekday()+1) % 7

        >>> ctool = CalendarTool()

        >>> ctool.getDayNumbers()[0] == fwday
        True
        """
        firstweekday = self._getCalendar().firstweekday()+1
        return [i%7 for i in range(firstweekday, firstweekday + 7)]

    security.declarePublic('getEventsForCalendar')
    def getEventsForCalendar(self, month='1', year='2002', **kw):
        """ recreates a sequence of weeks, by days each day is a mapping.
            {'day': #, 'url': None}
        """
        year = int(year)
        month = int(month)
        # daysByWeek is a list of days inside a list of weeks, like so:
        # [[0, 1, 2, 3, 4, 5, 6],
        #  [7, 8, 9, 10, 11, 12, 13],
        #  [14, 15, 16, 17, 18, 19, 20],
        #  [21, 22, 23, 24, 25, 26, 27],
        #  [28, 29, 30, 31, 0, 0, 0]]
        daysByWeek = self._getCalendar().monthcalendar(year, month)
        weeks = []

        events = self.catalog_getevents(year, month, **kw)

        for week in daysByWeek:
            days = []
            for day in week:
                if events.has_key(day):
                    days.append(events[day])
                else:
                    days.append({'day': day, 'event': 0, 'eventslist': []})

            weeks.append(days)

        return weeks

    security.declarePublic('catalog_getevents')
    def catalog_getevents(self, year, month, **kw):
        """ given a year and month return a list of days that have events
        """
        # XXX: this method violates the rules for tools/utilities:
        # it depends on a non-utility tool
        year = int(year)
        month = int(month)
        last_day = self._getCalendar().monthrange(year, month)[1]
        first_date = self.getBeginAndEndTimes(1, month, year)[0]
        last_date = self.getBeginAndEndTimes(last_day, month, year)[1]

        query_args = {
            'portal_type': self.getCalendarTypes(),
            'review_state': self.getCalendarStates(),
            'start': {'query': last_date, 'range': 'max'},
            'end': {'query': first_date, 'range': 'min'},
            'sort_on': 'start'}
        query_args.update(kw)

        ctool = getToolByName(self, 'portal_catalog')
        query = ctool(**query_args)

        # compile a list of the days that have events
        eventDays={}
        for daynumber in range(1, 32): # 1 to 31
            eventDays[daynumber] = {'eventslist': [],
                                    'event': 0,
                                    'day': daynumber}
        includedevents = []

        # prepare occurences
        all_events_occurences = []
        for result in query:
            # we presume that .occurences() returns occurences only for this month
            # TODO: the line below needs to be fixed to use the limit_start
            # and limit_end of occurences()
            occurences = IRecurrenceSupport(result.getObject()).occurences()[:3]
            for occurence in occurences:
                all_events_occurences.append(
                        dict(event=result,
                             start_date = occurence[0],
                             end_date = occurence[1]))

        for occurence in all_events_occurences:
            # TODO: 4 lines below need to be removed. Does this break anything?
            # It seems they are not needed: why would the catalog return
            # one event multiple times?
            # if occurence['event'].getRID() in includedevents:
            #     break
            # else:
            #     includedevents.append(occurence['event'].getRID())
            event={}
            # we need to deal with events that end next month
            if occurence['end_date'].month != month:
                # doesn't work for events that last ~12 months
                # fix it if it's a problem, otherwise ignore
                eventEndDay = last_day
                event['end'] = None
            else:
                eventEndDay = occurence['end_date'].day
                event['end'] = occurence['end_date'].strftime('%H:%M:%S')
            # and events that started last month
            if occurence['start_date'].month != month:  # same as above (12 month thing)
                eventStartDay = 1
                event['start'] = None
            else:
                eventStartDay = occurence['start_date'].day
                event['start'] = occurence['start_date'].strftime('%H:%M:%S')

            event['title'] = occurence['event'].Title or occurence['event'].getId

            if eventStartDay != eventEndDay:
                allEventDays = range(eventStartDay, eventEndDay+1)
                eventDays[eventStartDay]['eventslist'].append(
                        {'end': None,
                         'start': occurence['start_date'].strftime('%H:%M:%S'),
                         'title': event['title']})
                eventDays[eventStartDay]['event'] = 1

                for eventday in allEventDays[1:-1]:
                    eventDays[eventday]['eventslist'].append(
                        {'end': None,
                         'start': None,
                         'title': event['title']})
                    eventDays[eventday]['event'] = 1

                if occurence['end_date'] == occurence['end_date'].replace(hour=0, minute=0, second=0):
                    last_day_data = eventDays[allEventDays[-2]]
                    last_days_event = last_day_data['eventslist'][-1]
                    last_days_event['end'] = (occurence['end_date']-1).replace(hour=23, minute=59, second=59).strftime('%H:%M:%S')
                else:
                    eventDays[eventEndDay]['eventslist'].append(
                        {'end': occurence['end_date'].strftime('%H:%M:%S'),
                         'start': None, 'title': event['title']})
                    eventDays[eventEndDay]['event'] = 1
            else:
                eventDays[eventStartDay]['eventslist'].append(event)
                eventDays[eventStartDay]['event'] = 1
            # This list is not uniqued and isn't sorted
            # uniquing and sorting only wastes time
            # and in this example we don't need to because
            # later we are going to do an 'if 2 in eventDays'
            # so the order is not important.
            # example:  [23, 28, 29, 30, 31, 23]
        return eventDays


CalendarTool.__doc__ = BaseTool.__doc__

InitializeClass(CalendarTool)
