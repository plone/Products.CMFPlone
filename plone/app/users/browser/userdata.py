from zope.formlib import form

from zope.interface import Interface
from zope.interface import implements
from zope import schema

from plone.app.controlpanel import PloneMessageFactory as _
from plone.app.users.browser.schema_adapter import AccountPanelSchemaAdapter
from plone.app.users.browser.form import AccountPanelForm


class IUserDataSchema(Interface):

    fullname = schema.TextLine(title=_(u'label_full_name', default=u'Full Name'),
                               description=u'',
                               required=False)

    email = schema.TextLine(title=_(u'label_email', default=u'E-mail'),
                               description=u'',
                               required=True)

    home_page = schema.TextLine(title=_(u'label_homepage', default=u'Home page'),
                               description=_(u'help_homepage',
                                  default=u"The URL for your external home page, "
                                  "if you have one."),
                               required=False)

    location = schema.TextLine(title=_(u'label_location', default=u'Location'),
                               description=_(u'help_location', 
                                  default=u"Your location - either city and "
                                  "country - or in a company setting, where "
                                  "your office is located."),
                               required=False)


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
    label = _(u'User Data')
    description = _(u"From from which user can change its data.")
    form_name = _(u'User Data Form')

