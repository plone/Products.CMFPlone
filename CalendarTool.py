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

CalendarTool.__doc__ = BaseTool.__doc__

InitializeClass(CalendarTool)
