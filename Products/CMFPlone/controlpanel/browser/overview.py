from AccessControl import getSecurityManager
from Acquisition import aq_inner
from App.config import getConfiguration
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.registry.browser import controlpanel
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from ZPublisher.HTTPRequest import WSGIRequest

import pkg_resources
import warnings

try:
    import plone.app.event

    plone.app.event  # pyflakes
    HAS_PAE = True
except ImportError:
    HAS_PAE = False


class OverviewControlPanel(controlpanel.RegistryEditForm):

    template = ViewPageTemplateFile("overview.pt")

    base_category = "controlpanel"
    ignored_categories = "controlpanel_user"

    def __call__(self):
        self.request.set("disable_border", 1)
        return self.template()

    @memoize
    def cptool(self):
        return getToolByName(aq_inner(self.context), "portal_controlpanel")

    @memoize
    def migration(self):
        return getToolByName(aq_inner(self.context), "portal_migration")

    @memoize
    def core_versions(self):
        return self.migration().coreVersions()

    def pil(self):
        return "PIL" in self.core_versions()

    def server_info(self):
        wsgi = isinstance(self.request, WSGIRequest)
        server_name = "unknown"
        server_version = ""

        server_name = self.request.get("SERVER_SOFTWARE")
        if server_name:
            if "ZServer" in server_name:
                server_name = "ZServer"
            elif "/" in server_name:
                server_name = server_name.split("/")[0]
            try:
                server = pkg_resources.get_distribution(server_name)
                server_version = server.version
            except Exception:
                warnings.warn(
                    "Cannot find or parse version for %r"
                    % self.request.get("SERVER_SOFTWARE"),
                )
        return {
            "wsgi": wsgi,
            "server_name": server_name,
            "version": server_version,
        }

    def version_overview(self):

        core_versions = self.core_versions()
        versions = [
            "Plone {} ({})".format(
                core_versions["Plone"], core_versions["Plone Instance"]
            )
        ]

        for v in ("CMF", "Zope", "Python"):
            versions.append(v + " " + core_versions.get(v))
        pil = core_versions.get("PIL", None)
        if pil is not None:
            versions.append("PIL " + pil)
        return versions

    def is_dev_mode(self):
        return getConfiguration().debug_mode

    def upgrade_warning(self):
        mt = getToolByName(aq_inner(self.context), "portal_migration")
        if mt.needUpgrading():
            # if the user can't run the upgrade, no sense in displaying the
            # message
            sm = getSecurityManager()
            if sm.checkPermission(ManagePortal, self.context):
                return True
        return False

    def mailhost_warning(self):
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone", check=False)
        mailhost = mail_settings.smtp_host
        email = mail_settings.email_from_address
        if mailhost and email:
            return False
        return True

    def timezone_warning(self):
        """Returns true, if the portal_timezone is not set in the registry."""
        if not HAS_PAE:
            # No point of having a portal timezone configured without
            # plone.app.event installed.
            # TODO: Above applies to situation at time of writing. If other
            # datetimes outside plone.app.event use proper timezones too, the
            # HAS_PAE should be removed.
            return False
        # check if 'plone.portal_timezone' is in registry
        registry = getUtility(IRegistry)
        reg_key = "plone.portal_timezone"
        if reg_key not in registry:
            # else use 'plone.app.event.portal_timezone'
            # < Plone 5
            reg_key = "plone.app.event.portal_timezone"
        if reg_key not in registry:
            return True
        portal_timezone = registry[reg_key]
        if portal_timezone:
            return False
        return True  # No portal_timezone found.

    def categories(self):
        return self.cptool().getGroups()

    def sublists(self, category):
        return self.cptool().enumConfiglets(group=category)
