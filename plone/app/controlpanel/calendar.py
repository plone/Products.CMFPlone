from zope.interface import Interface
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Int
from zope.schema import Tuple

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from form import ControlPanelForm
from widgets import CalendarSessionWidget
from widgets import WeekdayWidget


class ICalendarSchema(Interface):

    calendar_types = Tuple(title=_(u'Types to show in the calendar.'),
                           description=_(u'Help?'),
                           required=True,
                           missing_value=set(),
                           value_type=Choice(
                               vocabulary="plone.app.vocabularies.PortalTypes"))

    calendar_states = Tuple(title=_(u'Workflow states to show in the calendar.'),
                            required=True,
                            missing_value=set(),
                            value_type=Choice(
                                vocabulary="plone.app.vocabularies.WorkflowStates"))

    firstweekday = Int(title=_(u'First day of week used in the calendar.'),
                       default=0,
                       required=True)

    use_session = Bool(title=_(u'Preserve selected year and month?'),
                       default=False,
                       required=True)


class CalendarControlPanelAdapter(SchemaAdapterBase):
    
    adapts(IPloneSiteRoot)
    implements(ICalendarSchema)

    def __init__(self, context):
        super(CalendarControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'portal_calendar')

    calendar_types = ProxyFieldProperty(ICalendarSchema['calendar_types'])
    calendar_states = ProxyFieldProperty(ICalendarSchema['calendar_states'])
    use_session = ProxyFieldProperty(ICalendarSchema['use_session'])
    firstweekday = ProxyFieldProperty(ICalendarSchema['firstweekday'])


class CalendarControlPanel(ControlPanelForm):

    form_fields = FormFields(ICalendarSchema)
    form_fields['use_session'].custom_widget = CalendarSessionWidget
    form_fields['firstweekday'].custom_widget = WeekdayWidget

    label = _("Calendar settings")
    description = None
    form_name = _("Calendar settings")
