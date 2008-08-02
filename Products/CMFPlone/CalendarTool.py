from Products.CMFCalendar.CalendarTool import CalendarTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

class CalendarTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.CalendarTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/event_icon.gif'

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

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

CalendarTool.__doc__ = BaseTool.__doc__

InitializeClass(CalendarTool)
