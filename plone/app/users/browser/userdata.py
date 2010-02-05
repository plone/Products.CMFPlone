from zope.formlib import form

from zope.interface import Interface
from zope.interface import implements

from Products.CMFPlone import PloneMessageFactory as _
from plone.app.users.browser.schema_adapter import AccountPanelSchemaAdapter
from plone.app.users.browser.account import AccountPanelForm
from plone.app.users.userdataschema import IUserDataSchema


class UserDataPanelAdapter(AccountPanelSchemaAdapter):

    implements(IUserDataSchema)

    def get_fullname(self):
        return self.context.getProperty('fullname', '')

    def set_fullname(self, value):
        return self.context.setMemberProperties({'fullname': value})

    fullname = property(get_fullname, set_fullname)


    def get_email(self):
        return self.context.getProperty('email', '')

    def set_email(self, value):
        return self.context.setMemberProperties({'email': value})

    email = property(get_email, set_email)


    def get_home_page(self):
        return self.context.getProperty('home_page', '')

    def set_home_page(self, value):
        return self.context.setMemberProperties({'home_page': value})

    home_page = property(get_home_page, set_home_page)


    def get_location(self):
        return self.context.getProperty('location', '')

    def set_location(self, value):
        return self.context.setMemberProperties({'location': value})

    location = property(get_location, set_location)

class UserDataPanel(AccountPanelForm):

    form_fields = form.FormFields(IUserDataSchema)
    label = _(u'title_personal_information_form', default=u'Personal information')
    description = _(u'description_personal_information_form', default='Change your personal information')
    form_name = _(u'User Data Form')

