# -*- coding: utf-8 -*-
from plone.app.robotframework.remote import RemoteLibrary

from zope.component.hooks import getSite
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IMailSchema


class CMFPloneRemoteKeywords(RemoteLibrary):
    """Robot Framework remote keywords library
    """

    def the_mail_setup_configured(self):
        registry = queryUtility(IRegistry)
        if registry is None:
            return
        mail_settings = registry.forInterface(IMailSchema, prefix='plone')
        if mail_settings is None:
            return
        mail_settings.smtp_host = u'localhost'
        mail_settings.email_from_address = 'john@doe.com'

    def the_self_registration_enabled(self):
        portal = getSite()
        app_perms = portal.rolesOfPermission(permission='Add portal member')
        reg_roles = []
        for appperm in app_perms:
            if appperm['selected'] == 'SELECTED':
                reg_roles.append(appperm['name'])

        reg_roles.append('Anonymous')

        portal.manage_permission(
            'Add portal member', roles=reg_roles, acquire=0)
