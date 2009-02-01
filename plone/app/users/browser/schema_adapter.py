#!/usr/bin/env python
# encoding: utf-8
"""
schema_adapter.py
"""

from zope.component import adapts
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from plone.app.controlpanel.utils import SchemaAdapterBase


class AccountPanelSchemaAdapter(SchemaAdapterBase):

    adapts(ISiteRoot)

    def __init__(self, context):

        mt = getToolByName(context, 'portal_membership')
        
        if mt.isAnonymousUser():
            raise "Can't modify properties of anonymous user"
        else:
            self.context = mt.getAuthenticatedMember()

