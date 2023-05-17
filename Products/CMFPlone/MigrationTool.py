from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from AccessControl.requestmethod import postonly
from App.config import getConfiguration
from io import StringIO
from OFS.SimpleItem import SimpleItem
from plone.base.interfaces import IMigrationTool
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.utils import UniqueObject
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from ZODB.POSException import ConflictError
from zope.interface import implementer

import logging
import pkg_resources
import sys
import transaction


logger = logging.getLogger("plone.app.upgrade")
_upgradePaths = {}


class Addon:
    """A profile or product.

    This is meant for core Plone packages, especially packages that
    are marked as not installable.  These are packages that an admin should
    not activate, deactivate or upgrade manually, but that should be
    handled by Plone.

    Most of this is already handled in plone.app.upgrade.  But when
    you have added an upgrade step to such a package, it can be hard
    to remember that you should also arrange that plone.app.upgrade
    applies this upgrade step.  This leads to an upgraded Plone Site
    where some core packages are not updated.  Or the upgrade handlers
    are run, but the version of the profile is not upgraded in the
    GenericSetup tool.
    """

    def __init__(self, profile_id=None, check_module=None):
        self.profile_id = profile_id
        self.check_module = check_module

    def __repr__(self):
        return f"<{self.__class__.__name__} profile {self.profile_id}>"

    def safe(self):
        # Is this addon safe to upgrade?

        # Is it safe to pass its profile id to
        # portal_setup.upgradeProfile?  That method checks if the
        # profile is 'unknown' and in this case does nothing.

        # But in some cases the profile may have been applied, but the
        # package is gone.  For that case, you can set
        # self.check_module.

        if self.check_module:
            # Can we import a module, as evidence that the code is
            # available?  Note that some modules may have been faked,
            # to avoid breakage.  For example on Plone 5.0 the
            # Products.TinyMCE module is faked by plone.app.upgrade.
            try:
                __import__(self.check_module)
            except ImportError:
                logger.info(
                    "Cannot import module %s. Ignoring %s", self.check_module, self
                )
                return False
        return True


class AddonList(list):
    def upgrade_all(self, context):
        setup = getToolByName(context, "portal_setup")
        for addon in self:
            if addon.safe():
                setup.upgradeProfile(addon.profile_id, quiet=True)


# List of upgradeable packages.  Obvious items to add here, are all
# core packages that actually have upgrade steps.
# Good start is portal_setup.listProfilesWithUpgrades()
# Please use 'check_module' for packages that are not direct dependencies
# of Products.CMFPlone, but of the Plone package.
ADDON_LIST = AddonList(
    [
        Addon(profile_id="Products.CMFEditions:CMFEditions"),
        Addon(
            profile_id="Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow",
            check_module="Products.CMFPlacefulWorkflow",
        ),
        Addon(profile_id="Products.PlonePAS:PlonePAS"),
        Addon(profile_id="plone.app.caching:default", check_module="plone.app.caching"),
        Addon(profile_id="plone.app.contenttypes:default"),
        Addon(profile_id="plone.app.dexterity:default"),
        Addon(profile_id="plone.app.discussion:default"),
        Addon(profile_id="plone.app.event:default"),
        Addon(profile_id="plone.app.iterate:default", check_module="plone.app.iterate"),
        Addon(profile_id="plone.app.multilingual:default"),
        Addon(profile_id="plone.app.querystring:default"),
        Addon(profile_id="plone.app.theming:default"),
        Addon(profile_id="plone.app.users:default"),
        Addon(profile_id="plone.restapi:default", check_module="plone.restapi"),
        Addon(profile_id="plone.session:default"),
        Addon(profile_id="plone.staticresources:default"),
        Addon(profile_id="plone.volto:default", check_module="plone.volto"),
        Addon(profile_id="plonetheme.barceloneta:default"),
    ]
)


@implementer(IMigrationTool)
class MigrationTool(PloneBaseTool, UniqueObject, SimpleItem):
    """Handles migrations between Plone releases"""

    id = "portal_migration"
    meta_type = "Plone Migration Tool"
    toolicon = "skins/plone_images/site_icon.png"

    manage_options = (
        {"label": "Upgrade", "action": "../@@plone-upgrade"},
    ) + SimpleItem.manage_options

    _needRecatalog = 0
    _needUpdateRole = 0

    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, "getInstanceVersion")

    def getInstanceVersion(self):
        # The version this instance of plone is on.
        setup = getToolByName(self, "portal_setup")
        version = setup.getLastVersionForProfile(_DEFAULT_PROFILE)
        if isinstance(version, tuple):
            version = ".".join(version)

        _version = getattr(self, "_version", None)
        if _version is None:
            self._version = False

        if version == "unknown":
            if _version:
                # Instance version was not pkg_resources compatible...
                _version = _version.replace("devel (svn/unreleased)", "dev")
                _version = _version.rstrip("-final")
                _version = _version.rstrip("final")
                _version = _version.replace("alpha", "a")
                _version = _version.replace("beta", "b")
                _version = _version.replace("-", ".")
                version = _version
            else:
                version = setup.getVersionForProfile(_DEFAULT_PROFILE)
            self.setInstanceVersion(version)
        return version

    security.declareProtected(ManagePortal, "setInstanceVersion")

    def setInstanceVersion(self, version):
        # The version this instance of plone is on.
        setup = getToolByName(self, "portal_setup")
        setup.setLastVersionForProfile(_DEFAULT_PROFILE, version)
        self._version = False

    security.declareProtected(ManagePortal, "getFileSystemVersion")

    def getFileSystemVersion(self):
        # The version this instance of plone is on.
        setup = getToolByName(self, "portal_setup")
        try:
            return setup.getVersionForProfile(_DEFAULT_PROFILE)
        except KeyError:
            pass
        return None

    security.declareProtected(ManagePortal, "getSoftwareVersion")

    def getSoftwareVersion(self):
        # The software version.
        dist = pkg_resources.get_distribution("Products.CMFPlone")
        return dist.version

    security.declareProtected(ManagePortal, "needUpgrading")

    def needUpgrading(self):
        # Need upgrading?
        return self.getInstanceVersion() != self.getFileSystemVersion()

    security.declareProtected(ManagePortal, "coreVersions")

    def coreVersions(self):
        # Useful core information.
        vars = {}
        get_dist = pkg_resources.get_distribution
        vars["Zope"] = get_dist("Zope").version
        vars["Python"] = sys.version
        vars["Platform"] = sys.platform
        vars["Plone"] = get_dist("Products.CMFPlone").version
        vars["Plone Instance"] = self.getInstanceVersion()
        vars["Plone File System"] = self.getFileSystemVersion()
        vars["CMF"] = get_dist("Products.CMFCore").version
        vars["Debug mode"] = getConfiguration().debug_mode and "Yes" or "No"
        try:
            vars["PIL"] = get_dist("PIL").version
        except pkg_resources.DistributionNotFound:
            try:
                vars["PIL"] = get_dist("PILwoTK").version
            except pkg_resources.DistributionNotFound:
                try:
                    vars["PIL"] = "%s (Pillow)" % get_dist("Pillow").version
                except pkg_resources.DistributionNotFound:
                    try:
                        import _imaging

                        _imaging  # pyflakes
                        vars["PIL"] = "unknown"
                    except ImportError:
                        pass

        return vars

    security.declareProtected(ManagePortal, "coreVersionsList")

    def coreVersionsList(self):
        # Useful core information.
        res = self.coreVersions().items()
        res.sort()
        return res

    security.declareProtected(ManagePortal, "needUpdateRole")

    def needUpdateRole(self):
        # Do roles need to be updated?
        return self._needUpdateRole

    security.declareProtected(ManagePortal, "needRecatalog")

    def needRecatalog(self):
        # Does this thing now need recataloging?
        return self._needRecatalog

    security.declareProtected(ManagePortal, "listUpgrades")

    def listUpgrades(self):
        # List available upgrade steps for our default profile.
        # Do not include upgrade steps for too new versions:
        # using a newer plone.app.upgrade version should not give problems.
        setup = getToolByName(self, "portal_setup")
        fs_version = self.getFileSystemVersion()
        upgrades = setup.listUpgrades(_DEFAULT_PROFILE, dest=fs_version)
        return upgrades

    security.declareProtected(ManagePortal, "upgrade")

    def upgrade(self, REQUEST=None, dry_run=None, swallow_errors=True):
        # Perform the upgrade.
        setup = getToolByName(self, "portal_setup")

        # This sets the profile version if it wasn't set yet
        version = self.getInstanceVersion()
        upgrades = self.listUpgrades()
        steps = []
        for u in upgrades:
            if isinstance(u, list):
                steps.extend(u)
            else:
                steps.append(u)

        try:
            stream = StringIO()
            handler = logging.StreamHandler(stream)
            handler.setLevel(logging.DEBUG)
            logger.addHandler(handler)
            gslogger = logging.getLogger("GenericSetup")
            gslogger.addHandler(handler)

            if dry_run:
                logger.info("Dry run selected.")

            logger.info("Starting the migration from version: %s" % version)

            for step in steps:
                try:
                    step["step"].doStep(setup)
                    setup.setLastVersionForProfile(_DEFAULT_PROFILE, step["dest"])
                    logger.info("Ran upgrade step: %s" % step["title"])
                except (ConflictError, KeyboardInterrupt):
                    raise
                except Exception:
                    logger.error("Upgrade aborted. Error:\n", exc_info=True)

                    if not swallow_errors:
                        raise
                    else:
                        # abort transaction to safe the zodb
                        transaction.abort()
                        break

            logger.info("End of upgrade path, main migration has finished.")

            if self.needUpgrading():
                logger.error("The upgrade path did NOT reach current version.")
                logger.error("Migration has failed")
            else:
                logger.info("Starting upgrade of core addons.")
                ADDON_LIST.upgrade_all(self)
                logger.info("Done upgrading core addons.")

                # do this once all the changes have been done
                if self.needRecatalog():
                    logger.info("Recatalog needed. This may take a while...")
                    try:
                        catalog = self.portal_catalog
                        # Reduce threshold for the reindex run
                        old_threshold = catalog.threshold
                        pg_threshold = getattr(catalog, "pgthreshold", 0)
                        catalog.pgthreshold = 300
                        catalog.threshold = 2000
                        catalog.refreshCatalog(clear=1)
                        catalog.threshold = old_threshold
                        catalog.pgthreshold = pg_threshold
                        self._needRecatalog = 0
                    except (ConflictError, KeyboardInterrupt):
                        raise
                    except Exception:
                        logger.error(
                            "Exception was thrown while cataloging:" "\n", exc_info=True
                        )
                        if not swallow_errors:
                            raise

                if self.needUpdateRole():
                    logger.info("Role update needed. This may take a while...")
                    try:
                        self.portal_workflow.updateRoleMappings()
                        self._needUpdateRole = 0
                    except (ConflictError, KeyboardInterrupt):
                        raise
                    except Exception:
                        logger.error(
                            "Exception was thrown while updating " "role mappings",
                            exc_info=True,
                        )
                        if not swallow_errors:
                            raise
                logger.info("Your Plone instance is now up-to-date.")

            if dry_run:
                logger.info("Dry run selected, transaction aborted")
                transaction.abort()

            return stream.getvalue()

        finally:
            logger.removeHandler(handler)
            gslogger.removeHandler(handler)

    upgrade = postonly(upgrade)


def registerUpgradePath(oldversion, newversion, function):
    """Basic register func"""
    pass


InitializeClass(MigrationTool)
registerToolInterface("portal_migration", IMigrationTool)
