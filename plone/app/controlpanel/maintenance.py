import time
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements
from zope.schema import Int
from App.config import getConfiguration

from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_hasattr
from plone.fieldsets.form import FieldsetsEditForm
from plone.app.controlpanel.interfaces import IPloneControlPanelForm


class IMaintenanceSchema(Interface):

    days = Int(title=_(u'Number of days to keep'),
        description=_(u'Select the number of days history to keep'),
        default=7,
        required=True)


class MaintenanceControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IMaintenanceSchema)
    
    def __init__(self, context):
        pprop = getToolByName(context, 'portal_properties')
        self.context = pprop.site_properties
        self.cpanel = context.unrestrictedTraverse('/Control_Panel')
        
    def get_days(self):
        return self.context.number_of_days_to_keep
        
    def set_days(self, value):
        if type(value) == type(''):
            value = int(value)
        # skip the actual pack method in tests
        if not value == -1:
            self.cpanel.manage_pack(days=value, REQUEST=None)
        self.context.number_of_days_to_keep = value

    days = property(get_days, set_days)


class MaintenanceControlPanel(FieldsetsEditForm):
    """A simple form to pack the databases."""

    implements(IPloneControlPanelForm)

    template = ZopeTwoPageTemplateFile('control-panel.pt')
    form_fields = form.FormFields(IMaintenanceSchema)
    label = _("Database maintenance")
    description = _("""The Zope Database is a transactional database, which results in
                       deleted items and previous versions of items being kept. Packing
                       the database will actually delete the history to a certain point
                       in time and free diskspace used.""")
    form_name = _("Start packing")

    @form.action(_(u'Pack'))
    def handle_edit_action(self, action, data):
        form.applyChanges(self.context, self.form_fields, data, self.adapters)
        self.status = _("Packed the database.")
    

