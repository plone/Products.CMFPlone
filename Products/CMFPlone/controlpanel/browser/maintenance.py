from AccessControl import getSecurityManager
from AccessControl.Permissions import view_management_screens
from Acquisition import aq_inner
from App.config import getConfiguration
from plone.autoform.form import AutoExtensibleForm
from plone.base import PloneMessageFactory as _
from plone.base.interfaces import IMaintenanceSchema
from plone.memoize.view import memoize
from plone.protect import CheckAuthenticator
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form import form
from zope.component import getMultiAdapter

import logging
import os
import time


LIFETIME = True
try:
    from Lifetime import shutdown
except ImportError:
    LIFETIME = False

try:
    from html import escape
except ImportError:
    from cgi import escape


logger = logging.getLogger(__file__)


class MaintenanceControlPanel(AutoExtensibleForm, form.EditForm):
    """A simple form to pack the databases."""

    schema = IMaintenanceSchema
    id = "maintenance-control-panel"
    label = _("Maintenance Settings")
    description = _("Zope server and site maintenance options.")
    form_name = _("Zope Database Packing")
    control_panel_view = "maintenance-controlpanel"
    template = ViewPageTemplateFile("maintenance.pt")

    @memoize
    def portal(self):
        portal_state = getMultiAdapter(
            (aq_inner(self.context), self.request), name="plone_portal_state"
        )
        return portal_state.portal()

    @button.buttonAndHandler(_("Pack database now"), name="pack")
    def handle_pack_action(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        CheckAuthenticator(self.request)
        if not self.available():
            self.status = _(
                "text_not_allowed_manage_server",
                default="You are not allowed to manage the Zope server.",
            )
            return

        days = data.get("days", None)
        # skip the actual pack method in tests
        if days is not None and isinstance(days, int) and days >= 0:
            db = self.portal()._p_jar.db()
            t = time.time() - (days * 86400)
            db.pack(t)
        self.status = _("Packed the database.")

    @button.buttonAndHandler(_("Shut down"), name="shutdown")
    def handle_shutdown_action(self, action):
        CheckAuthenticator(self.request)
        if not self.available():
            self.status = _(
                "text_not_allowed_manage_server",
                default="You are not allowed to manage the Zope server.",
            )
            return
        try:
            user = '"%s"' % getSecurityManager().getUser().getUserName()
        except Exception:
            user = "unknown user"
        logger.info("Shutdown requested by %s" % user)
        if LIFETIME:
            shutdown(0)
        else:
            raise
        # TODO: returning html has no effect in button handlers
        self.request.response.setHeader("X-Theme-Disabled", "True")
        return """<html><head></head><body>{}</body></html>""".format(
            _("plone_shutdown", default="Zope is shutting down.")
        )

    @button.buttonAndHandler(_("Restart"), name="restart")
    def handle_restart_action(self, action):
        CheckAuthenticator(self.request)
        if not self.available():
            self.status = _(
                "text_not_allowed_manage_server",
                default="You are not allowed to manage the Zope server.",
            )
            return

        try:
            user = '"%s"' % getSecurityManager().getUser().getUserName()
        except Exception:
            user = "unknown user"
        logger.info("Restart requested by %s" % user)
        shutdown(1)
        url = self.request.get("URL")
        # TODO: returning html has no effect in button handlers
        self.request.response.setHeader("X-Theme-Disabled", "True")
        return """<html><head>
            <meta http-equiv="refresh" content="5; url={}">
        </head><body>{}</body></html>""".format(
            escape(url, 1),
            _(
                "plone_restarting",
                default="Zope is restarting. This page will refresh in 30"
                " seconds...",
            ),
        )

    def available(self):
        root = aq_inner(self.context).getPhysicalRoot()
        sm = getSecurityManager()
        return sm.checkPermission(view_management_screens, root)

    def isRestartable(self):
        if "ZMANAGED" in os.environ:
            return True
        return False

    def isDevelopmentMode(self):
        return bool(getConfiguration().debug_mode)

    def coreVersions(self):
        mt = getToolByName(self.context, "portal_migration")
        versions = mt.coreVersions()
        versions["Instance"] = versions["Plone Instance"]
        return versions

    def dbName(self):
        return self.portal()._p_jar.db().database_name

    def dbSize(self):
        size = self.portal()._p_jar.db().getSize()

        # From Zope2.App.ApplicationManager
        if type(size) is str:
            return size

        if size >= 1048576.0:
            return "%.1f MB" % (size / 1048576.0)
        return "%.1f kB" % (size / 1024.0)
