# -*- coding: utf-8 -*-
from z3c.form import button
import os
from cgi import escape

from z3c.form import form

from AccessControl import getSecurityManager
from AccessControl.Permissions import view_management_screens
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IMaintenanceSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.autoform.form import AutoExtensibleForm
from plone.protect import CheckAuthenticator


class MaintenanceControlPanel(AutoExtensibleForm, form.EditForm):
    """A simple form to pack the databases."""

    schema = IMaintenanceSchema
    id = "maintenance-control-panel"
    label = _(u'Maintenance Settings')
    description = _(u"Zope server and site maintenance options.")
    form_name = _(u'Zope Database Packing')
    control_panel_view = "maintenance-controlpanel"
    template = ViewPageTemplateFile('maintenance.pt')

    @button.buttonAndHandler(_(u'Pack database now'), name='pack')
    def handle_edit_action(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        CheckAuthenticator(self.request)
        if not self.available():
            self.status = _(
                u'text_not_allowed_manage_server',
                default=u'You are not allowed to manage the Zope server.'
            )
            return

        value = data.get('days', None)
        # skip the actual pack method in tests
        if value is not None and isinstance(value, int) and value >= 0:
            context = aq_inner(self.context)
            cpanel = context.unrestrictedTraverse('/Control_Panel')
            cpanel.manage_pack(days=value, REQUEST=None)
        self.status = _(u'Packed the database.')

    @button.buttonAndHandler(_(u'Shut down'), name='shutdown')
    def handle_shutdown_action(self, action):
        CheckAuthenticator(self.request)
        if not self.available():
            self.status = _(
                u'text_not_allowed_manage_server',
                default=u'You are not allowed to manage the Zope server.'
            )
            return
        context = aq_inner(self.context)
        cpanel = context.unrestrictedTraverse('/Control_Panel')
        result = cpanel.manage_shutdown()
        return result

    @button.buttonAndHandler(_(u'Restart'), name='restart')
    def handle_restart_action(self, action):
        CheckAuthenticator(self.request)
        if not self.available():
            self.status = _(
                u'text_not_allowed_manage_server',
                default=u'You are not allowed to manage the Zope server.'
            )
            return
        context = aq_inner(self.context)
        cpanel = context.unrestrictedTraverse('/Control_Panel')
        url = self.request.get('URL')
        cpanel.manage_restart(url)
        return """<html>
        <head><meta HTTP-EQUIV=REFRESH CONTENT="30; URL=%s">
        </head>
        <body>
            Zope is restarting. This page will refresh in 30 seconds...
        </body>
        </html>
        """ % escape(url, 1)

    def available(self):
        root = aq_inner(self.context).getPhysicalRoot()
        sm = getSecurityManager()
        return sm.checkPermission(view_management_screens, root)

    def isRestartable(self):
        if 'ZMANAGED' in os.environ:
            return True
        return False

    def isDevelopmentMode(self):
        qi = getToolByName(self.context, 'portal_quickinstaller')
        return qi.isDevelopmentMode()

    def coreVersions(self):
        mt = getToolByName(self.context, 'portal_migration')
        versions = mt.coreVersions()
        versions['Instance'] = versions['Plone Instance']
        return versions

    def processTime(self):
        context = aq_inner(self.context)
        cpanel = context.unrestrictedTraverse('/Control_Panel')
        return cpanel.process_time()

    def dbSize(self):
        context = aq_inner(self.context)
        cpanel = context.unrestrictedTraverse('/Control_Panel')
        return cpanel.db_size()
