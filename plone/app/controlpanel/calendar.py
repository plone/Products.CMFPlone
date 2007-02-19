from zope.interface import Interface
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Choice
from zope.schema import Int
from zope.schema import Tuple

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from form import ControlPanelForm
from widgets import WeekdayWidget


class ICalendarSchema(Interface):

    calendar_states = Tuple(title=_(u'Workflow states to show in the calendar.'),
                            required=True,
                            missing_value=set(),
                            value_type=Choice(
                                vocabulary="plone.app.vocabularies.WorkflowStates"))

    firstweekday = Int(title=_(u'First day of week used in the calendar.'),
                       default=0,
                       required=True)


class CalendarControlPanelAdapter(SchemaAdapterBase):
    
    adapts(IPloneSiteRoot)
    implements(ICalendarSchema)

    def __init__(self, context):
        super(CalendarControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'portal_calendar')

    calendar_states = ProxyFieldProperty(ICalendarSchema['calendar_states'])
    firstweekday = ProxyFieldProperty(ICalendarSchema['firstweekday'])


class CalendarControlPanel(ControlPanelForm):

    form_fields = FormFields(ICalendarSchema)
    form_fields['firstweekday'].custom_widget = WeekdayWidget

    label = _("Calendar settings")
    description = None
    form_name = _("Calendar settings")
