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
from zope.schema import TextLine

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from plone.app.controlpanel import PloneMessageFactory as _
from plone.app.controlpanel.utils import SchemaAdapterBase
from plone.app.users.browser.form import AccountPanelForm


class IUserDataSchema(Interface):

    fullname = TextLine(title=_(u'Full Name'))

class UserDataPanelAdapter(SchemaAdapterBase):

    adapts(ISiteRoot)
    implements(IUserDataSchema)

    def __init__(self, context):
        self.context = getToolByName(context, 'portal_memberdata')

    def get_fullname(self):
        return 'Muhaha'

    def set_fullname(self, value):
        setDefaultContentType(self.context, value)

    fullname = property(get_fullname, set_fullname)

class UserDataPanel(AccountPanelForm):

    form_fields = form.FormFields(IUserDataSchema)
    label = _(u'User Data')
    description = _(u"From from which user can change its data.")
    form_name = _(u'User Data Form')

