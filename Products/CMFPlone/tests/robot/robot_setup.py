# -*- coding: utf-8 -*-
from plone.app.robotframework.remote import RemoteLibrary

from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName


class CMFPloneRemoteKeywords(RemoteLibrary):
    """Robot Framework remote keywords library
    """

    def the_mail_setup_configured(self):
        portal = getSite()
        mailhost = getToolByName(portal, 'MailHost')
        mailhost.smtp_host = 'localhost'
        portal.email_from_address = 'dummyme@dummy.com'
        portal.email_from_name = 'me'

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
