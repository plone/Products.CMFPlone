from Products.CMFCalendar.CalendarTool import CalendarTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class CalendarTool(BaseTool):

    meta_type = ToolNames.CalendarTool
    security = ClassSecurityInfo()

CalendarTool.__doc__ = BaseTool.__doc__

InitializeClass(CalendarTool)
