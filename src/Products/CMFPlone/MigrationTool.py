from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from AccessControl.requestmethod import postonly
from App.config import getConfiguration
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as dist_version
from io import StringIO
from OFS.SimpleItem import SimpleItem
from plone.base.interfaces import IMigrationTool
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.utils import UniqueObject
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from ZODB.POSException import ConflictError
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface

import logging
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


class IAddonList(Interface):
    """Utility providing a list of add-ons managed by the migration tool."""

    addon_list: AddonList


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
        Addon(
            profile_id="plone.app.multilingual:default",
            check_module="plone.app.multilingual",
        ),
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


@implementer(IAddonList)
class LocalAddonList:
    addon_list = ADDON_LIST


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

    @property
    def setup(self):
        # Get the portal_setup tool.
        # Note: depending on the acquisition chain, sometimes
        # getToolByName(self, "portal_setup") works, sometimes not.
        # So we always get the site.
        site = getSite()
        return getToolByName(site, "portal_setup")

    @property
    def profile(self):
        context_id = self.setup.getBaselineContextID()
        prefix = "profile-"
        if context_id.startswith(prefix):
            context_id = context_id[len(prefix) :]
        return context_id

    @property
    def package_name(self):
        # Products.CMFPlone:plone -> Products.CMFPlone
        return self.profile.partition(":")[0]

    @security.protected(ManagePortal)
    def getInstanceVersion(self):
        # Get the version of the base profile this Plone instance is on.
        setup = self.setup
        version = setup.getLastVersionForProfile(self.profile)
        if isinstance(version, tuple):
            version = ".".join(version)
        if version == "unknown":
            version = setup.getVersionForProfile(self.profile)
            self.setInstanceVersion(version)
        return version

    @security.protected(ManagePortal)
    def setInstanceVersion(self, version):
        # Set the version of the base profile for this Plone instance.
        self.setup.setLastVersionForProfile(self.profile, version)

    @security.protected(ManagePortal)
    def getFileSystemVersion(self):
        # Get the version of the base profile that is available on the
        # filesystem.
        try:
            return self.setup.getVersionForProfile(self.profile)
        except KeyError:
            pass
        return None

    @security.protected(ManagePortal)
    def getSoftwareVersion(self):
        # Get the software version of the Python package that contains the
        # base profile for this Plone instance.
        try:
            return dist_version(self.package_name)
        except PackageNotFoundError:
            logger.error(
                "No distribution found for package %s (base profile %s).",
                self.package_name,
                self.profile,
            )
            return None

    @security.protected(ManagePortal)
    def needUpgrading(self):
        # Need upgrading?
        return self.getInstanceVersion() != self.getFileSystemVersion()

    @security.protected(ManagePortal)
    def coreVersions(self):
        # Useful core information.
        vars = {}
        vars["Zope"] = dist_version("Zope")
        vars["Python"] = sys.version
        vars["Platform"] = sys.platform
        vars["Plone"] = dist_version("Products.CMFPlone")
        # The next few belong to the base profile:
        vars["Plone Instance"] = self.getInstanceVersion()
        vars["Plone File System"] = self.getFileSystemVersion()
        vars["core_package"] = self.package_name
        vars["core_version"] = self.getSoftwareVersion()
        vars["CMF"] = dist_version("Products.CMFCore")
        vars["Debug mode"] = getConfiguration().debug_mode and "Yes" or "No"
        try:
            vars["PIL"] = "%s (Pillow)" % dist_version("Pillow")
        except PackageNotFoundError:
            pass
        return vars

    @security.protected(ManagePortal)
    def coreVersionsList(self):
        # Useful core information.
        return sorted(self.coreVersions().items())

    @security.protected(ManagePortal)
    def needUpdateRole(self):
        # Do roles need to be updated?
        return self._needUpdateRole

    @security.protected(ManagePortal)
    def needRecatalog(self):
        # Does this thing now need recataloging?
        return self._needRecatalog

    @security.protected(ManagePortal)
    def listUpgrades(self):
        # List available upgrade steps for our default profile.
        # Do not include upgrade steps for too new versions:
        # using a newer plone.app.upgrade version should not give problems.
        fs_version = self.getFileSystemVersion()
        upgrades = self.setup.listUpgrades(self.profile, dest=fs_version)
        return upgrades

    @security.protected(ManagePortal)
    def list_steps(self):
        upgrades = self.listUpgrades()
        steps = []
        for upgrade in upgrades:
            if isinstance(upgrade, list):
                steps.extend(upgrade)
            else:
                steps.append(upgrade)
        return steps

    @property
    def addon_list(self) -> AddonList:
        utility = queryUtility(IAddonList, self.package_name)
        if utility is None:
            utility = queryUtility(IAddonList, "Products.CMFPlone")
            if utility is None:
                return AddonList()
        return utility.addon_list

    def _upgrade_run_steps(self, steps, swallow_errors=True):
        setup = self.setup
        for step in steps:
            try:
                step["step"].doStep(setup)
                setup.setLastVersionForProfile(self.profile, step["dest"])
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

    def _upgrade_recatalog(self, swallow_errors=True):
        if not self.needRecatalog():
            return
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
            logger.error("Exception was thrown while cataloging:\n", exc_info=True)
            if not swallow_errors:
                raise

    def _upgrade_roles(self, swallow_errors=True):
        if not self.needUpdateRole():
            return
        logger.info("Role update needed. This may take a while...")
        try:
            self.portal_workflow.updateRoleMappings()
            self._needUpdateRole = 0
        except (ConflictError, KeyboardInterrupt):
            raise
        except Exception:
            logger.error(
                "Exception was thrown while updating role mappings",
                exc_info=True,
            )
            if not swallow_errors:
                raise

    @security.protected(ManagePortal)
    def upgrade(self, REQUEST=None, dry_run=None, swallow_errors=True):
        # Perform the upgrade.

        # This sets the profile version if it wasn't set yet
        version = self.getInstanceVersion()
        steps = self.list_steps()

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
            self._upgrade_run_steps(steps, swallow_errors=swallow_errors)
            logger.info("End of upgrade path, main migration has finished.")

            if self.needUpgrading():
                logger.error("The upgrade path did NOT reach current version.")
                logger.error("Migration has failed")
            else:
                logger.info("Starting upgrade of core addons.")
                self.addon_list.upgrade_all(self)
                logger.info("Done upgrading core addons.")

                # do this once all the changes have been done
                self._upgrade_recatalog(swallow_errors=swallow_errors)
                self._upgrade_roles(swallow_errors=swallow_errors)

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
