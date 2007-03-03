from plone.fieldsets.form import FieldsetsEditForm
from zope.component import adapts
from zope.formlib import form
from zope.interface import Interface
from zope.interface import implements
from zope.schema import Int

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from plone.app.controlpanel.interfaces import IPloneControlPanelForm


class IMaintenanceSchema(Interface):

    days = Int(title=_(u"Number of days to keep"),
        description=_(u"The Zope Database keeps deleted and previous versions "
                       "of objects. Packing the database will actually delete "
                       "these to a certain point in time and free diskspace."),
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

    template = ZopeTwoPageTemplateFile('maintenance.pt')
    form_fields = form.FormFields(IMaintenanceSchema)
    label = _(u'Maintenance')
    description = _(u"Zope server and site maintenance options.")
    form_name = _(u'Start packing')

    @form.action(_(u'Pack'))
    def handle_edit_action(self, action, data):
        form.applyChanges(self.context, self.form_fields, data, self.adapters)
        self.status = _(u'Packed the database.')

    def isDevelopmentMode(self):
        qi = getToolByName(aq_inner(self.context), 'portal_quickinstaller')
        return qi.isDevelopmentMode()

    def coreVersions(self):
        mt = getToolByName(aq_inner(self.context), 'portal_migration')
        versions = mt.coreVersions()
        versions['Instance'] = versions['Plone Instance']
        return versions
