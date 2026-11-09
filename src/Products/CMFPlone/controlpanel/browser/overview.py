from AccessControl import getSecurityManager
from Acquisition import aq_inner
from App.config import getConfiguration
from datetime import date
from importlib.metadata import distribution
from plone.app.registry.browser import controlpanel
from plone.base.interfaces.controlpanel import IMailSchema
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from ZPublisher.HTTPRequest import WSGIRequest

import sys
import warnings

try:
    import plone.app.event

    plone.app.event  # pyflakes
    HAS_PAE = True
except ImportError:
    HAS_PAE = False


# When is a Python 3 minor version out of support?
# See https://devguide.python.org/versions/#versions
_PYTHON_MINOR_OUT_OF_SUPPORT = {
    10: date(2026, 10, 1),
    11: date(2027, 10, 1),
    12: date(2028, 10, 1),
    13: date(2029, 10, 1),
    14: date(2030, 10, 1),
    15: date(2031, 10, 1),
}
# These dates are specific to the current Plone minor version.
# See https://plone.org/download/release-schedule
# Plone 6.2 has maintenance support until Plone 6.3.0 or 7.0.0 comes out.
# There is no fixed date for this yet.
_PLONE_OUT_OF_MAINTENANCE_SUPPORT = None
# Security support is at least until 2027-12-31 (5 years from 6.0.0).
# This may be extended until the release of Plone 7.0.0, expected mid 2028.
_PLONE_OUT_OF_SECURITY_SUPPORT = date(2027, 12, 31)


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
                server = distribution(server_name)
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
        versions = []
        core_package = core_versions.get("core_package")
        if core_package and core_package != "Products.CMFPlone":
            # We have a different base profile.
            # Show info from its package and from Products.CMFPlone.
            name = core_versions["core_package"]
            package_version = core_versions["core_version"]
            metadata_version = core_versions["Plone Instance"]
            versions.append(f"{name} {package_version} ({metadata_version})")
            versions.append(f"Plone {core_versions['Plone']}")
        else:
            name = "Plone"
            package_version = core_versions["Plone"]
            metadata_version = core_versions["Plone Instance"]
            versions.append(f"{name} {package_version} ({metadata_version})")
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

    def python_warning(self):
        minor_version = sys.version_info.minor
        deadline = _PYTHON_MINOR_OUT_OF_SUPPORT.get(minor_version)
        if not deadline:
            # This Python version is not supported at all
            return True
        # Warn when today is on or after the deadline for this minor version.
        return date.today() >= deadline

    def plone_maintenance_warning(self):
        if _PLONE_OUT_OF_MAINTENANCE_SUPPORT is None:
            return False
        return date.today() > _PLONE_OUT_OF_MAINTENANCE_SUPPORT

    def plone_security_warning(self):
        return date.today() > _PLONE_OUT_OF_SECURITY_SUPPORT

    def version_warning(self):
        # Is there *any* version warning?
        return (
            self.python_warning()
            or self.plone_maintenance_warning()
            or self.plone_security_warning()
        )

    def categories(self):
        return self.cptool().getGroups()

    def sublists(self, category):
        return self.cptool().enumConfiglets(group=category)
