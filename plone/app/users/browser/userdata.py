#!/usr/bin/env python
# encoding: utf-8
"""
userdata.py
"""

#import warnings
#from zope.component import queryAdapter
#from zope.component import queryUtility
#from zope.interface import implements

#from Acquisition import aq_inner, aq_base
#from Products.CMFPlone import utils
#from Products.Five.browser import BrowserView

#from plone.app.users.browser.interfaces import IPersonalPreferencesPanel

from zope.formlib import form

from zope.interface import Interface
from zope.component import adapts
from zope.interface import implements
from zope import schema

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from plone.app.controlpanel import PloneMessageFactory as _
from plone.app.controlpanel.utils import SchemaAdapterBase
from plone.app.users.browser.form import AccountPanelForm


class IUserDataSchema(Interface):

    fullname = schema.TextLine(title=_(u'Full Name'))

    email = schema.TextLine(title=u'Email',
                               description=u'')

    home_page = schema.TextLine(title=u'Home page',
                               description=u'The URL for your external home page, if you have one.')

    location = schema.TextLine(title=u'Location',
                               description=u'Your location - either city and country - or in a company setting, where your office is located.')


class UserDataPanelAdapter(SchemaAdapterBase):

    adapts(ISiteRoot)
    implements(IUserDataSchema)

    def __init__(self, context):

        mt = getToolByName(context, 'portal_membership')
        
        if mt.isAnonymousUser():
            raise "Can't modify properties of anonymous user"
        else:
            self.context = mt.getAuthenticatedMember()


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

