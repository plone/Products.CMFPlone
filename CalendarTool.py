import calendar
from Products.CMFCalendar.CalendarTool import CalendarTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.utils import classImplements

class CalendarTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.CalendarTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/event_icon.gif'

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

    security.declarePublic('getDayNumbers')
    def getDayNumbers(self):
        """ Returns a list of daynumbers with the correct start day first """
        firstweekday = calendar.firstweekday()+1
        return [i%7 for i in range(firstweekday, firstweekday + 7)]

CalendarTool.__doc__ = BaseTool.__doc__

classImplements(CalendarTool, CalendarTool.__implements__)
InitializeClass(CalendarTool)
