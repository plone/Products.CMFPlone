from zope.component import adapts
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.controlpanel.form import ControlPanelForm
from registrationschema import IRegistrationSchema, UserDataWidget
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

# Property as it is named in portal_properties
USER_REGISTRATION_FIELDS = 'user_registration_fields'

_ = MessageFactory('plone')

class RegistrationControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IRegistrationSchema)

    def __init__(self, context):
        super(RegistrationControlPanelAdapter, self).__init__(context)
        pprop = getToolByName(context, 'portal_properties')
        self.context = pprop.site_properties

    def set_userRegistrationfields(self, value):

        self.context._updateProperty(USER_REGISTRATION_FIELDS, value)


    def get_userRegistrationfields(self):

        return self.context.getProperty(USER_REGISTRATION_FIELDS,[])

    user_registration_fields = property(get_userRegistrationfields, set_userRegistrationfields)



class RegistrationControlPanel(ControlPanelForm):

    base_template = ControlPanelForm.template
    template = ZopeTwoPageTemplateFile('memberregistration.pt')

    form_fields = form.FormFields(IRegistrationSchema)

    form_fields['user_registration_fields'].custom_widget = UserDataWidget

    label = _(u"Registration settings")
    description = _(u"Registration settings for this site.")
    form_name = _(u"Registration settings")
