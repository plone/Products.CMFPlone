from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from AccessControl.requestmethod import postonly
from App.config import getConfiguration
from collections.abc import Generator
from contextlib import contextmanager
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as dist_version
from io import StringIO
from OFS.SimpleItem import SimpleItem
from OFS.Traversable import Traversable
from plone.base.interfaces import IMigrationTool
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.utils import UniqueObject
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.GenericSetup.tool import SetupTool
from ZODB.POSException import ConflictError
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface
from typing import TypedDict
import logging
import sys
import transaction


logger = logging.getLogger("plone.app.upgrade")
_upgradePaths = {}


def _pil_version() -> str:
    """Return version of the image package being used."""
    version = "unknown"
    try:
        version = dist_version("PIL")
    except PackageNotFoundError:
        try:
            version = dist_version("PILwoTK")
        except PackageNotFoundError:
            try:
                vars["PIL"] = "%s (Pillow)" % dist_version("Pillow")
            except PackageNotFoundError:
                try:
                    import _imaging

                    _imaging  # pyflakes
                except ImportError:
                    pass
    return version


@contextmanager
def get_logger(stream: StringIO) -> Generator[logging.Logger]:
    """Setup logging during migration."""
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    gslogger = logging.getLogger("GenericSetup")
    gslogger.addHandler(handler)
    try:
        yield logger
    finally:
        # Remove new handler
        logger.removeHandler(handler)
        gslogger.removeHandler(handler)


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

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} profile {self.profile_id}>"

    def safe(self) -> bool:
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
                    f"Cannot import module {self.check_module}. Ignoring {self}"
                )
                return False
        return True


class AddonList(list):

    def upgrade_all(self, context: Traversable) -> None:
        setup = getToolByName(context, "portal_setup")
        for addon in self:
            if addon.safe():
                setup.upgradeProfile(addon.profile_id, quiet=True)


class IAddonList(Interface):
    """Utility providing a list of add ons managed by the migration tool."""

    addon_list: AddonList


@implementer(IAddonList)
class LocalAddonList:
    # List of upgradeable packages.  Obvious items to add here, are all
    # core packages that actually have upgrade steps.
    # Good start is portal_setup.listProfilesWithUpgrades()
    # Please use 'check_module' for packages that are not direct dependencies
    # of Products.CMFPlone, but of the Plone package
    addon_list: AddonList = AddonList(
        [
            Addon(profile_id="Products.CMFEditions:CMFEditions"),
            Addon(
                profile_id="Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow",
                check_module="Products.CMFPlacefulWorkflow",
            ),
            Addon(profile_id="Products.PlonePAS:PlonePAS"),
            Addon(
                profile_id="plone.app.caching:default", check_module="plone.app.caching"
            ),
            Addon(profile_id="plone.app.contenttypes:default"),
            Addon(profile_id="plone.app.dexterity:default"),
            Addon(profile_id="plone.app.discussion:default"),
            Addon(profile_id="plone.app.event:default"),
            Addon(
                profile_id="plone.app.iterate:default", check_module="plone.app.iterate"
            ),
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


_DEFAULT_PACKAGE_NAME = "Products.CMFPlone"
_DEFAULT_FRIENDLY_NAME = "Plone"


class CoreVersionInformation(TypedDict):
    name: str
    package_name: str
    package_version: str
    instance_version: str
    fs_version: str


VersionInformation = TypedDict(
    "VersionInformation",
    {
        "Python": str,
        "Zope": str,
        "Platform": str,
        "CMFPlone": str,
        "Plone": str,
        "Plone Instance": str,
        "Plone File System": str,
        "CMF": str,
        "Debug mode": str,
        "PIL": str,
        "core": CoreVersionInformation,
        "packages": dict[str, str],
    },
)


@implementer(IMigrationTool)
class MigrationTool(PloneBaseTool, UniqueObject, SimpleItem):
    """Handles migrations between Plone releases"""

    id: str = "portal_migration"
    meta_type: str = "Plone Migration Tool"
    toolicon: str = "skins/plone_images/site_icon.png"

    profile: str = _DEFAULT_PROFILE
    package_name: str = _DEFAULT_PACKAGE_NAME
    friendly_name: str = _DEFAULT_FRIENDLY_NAME

    manage_options: tuple[dict[str, str], ...] = (
        {"label": "Upgrade", "action": "../@@plone-upgrade"},
    ) + SimpleItem.manage_options

    _needRecatalog: int = 0
    _needUpdateRole: int = 0

    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, "initializeTool")

    @property
    def setup(self) -> SetupTool:
        site = getSite()
        return getToolByName(site, "portal_setup")

    def initializeTool(self, profile: str, package_name: str, friendly_name: str = ""):
        """Initialize the migration tool."""
        self.profile = profile
        self.package_name = package_name
        self.friendly_name = friendly_name if friendly_name else package_name

    @property
    def addon_list(self) -> AddonList:
        utility = getUtility(IAddonList, self.package_name)
        return utility.addon_list

    security.declareProtected(ManagePortal, "getInstanceVersion")

    def getInstanceVersion(self) -> str:
        # The version this instance of plone is on.
        setup = self.setup
        profile = self.profile
        version = setup.getLastVersionForProfile(profile)
        if isinstance(version, tuple):
            version = ".".join(version)

        _version = getattr(self, "_version", None)
        if _version is None:
            self._version = False

        if version == "unknown":
            if _version:
                # Instance version was not standard...
                _version = _version.replace("devel (svn/unreleased)", "dev")
                _version = _version.rstrip("-final")
                _version = _version.rstrip("final")
                _version = _version.replace("alpha", "a")
                _version = _version.replace("beta", "b")
                _version = _version.replace("-", ".")
                version = _version
            else:
                version = setup.getVersionForProfile(profile)
            self.setInstanceVersion(version)
        return version

    security.declareProtected(ManagePortal, "setInstanceVersion")

    def setInstanceVersion(self, version: str) -> None:
        # The version this instance of plone is on.
        setup = self.setup
        setup.setLastVersionForProfile(self.profile, version)
        self._version = False

    security.declareProtected(ManagePortal, "getFileSystemVersion")

    def getFileSystemVersion(self) -> str | None:
        # The version this instance of plone is on.
        setup = self.setup
        try:
            return setup.getVersionForProfile(self.profile)
        except KeyError:
            pass
        return None

    security.declareProtected(ManagePortal, "getSoftwareVersion")

    def getSoftwareVersion(self) -> str:
        # The software version.
        try:
            return dist_version(self.package_name)
        except PackageNotFoundError:
            # Fall back to CMFPlone for backward compatibility
            return dist_version(_DEFAULT_PACKAGE_NAME)

    security.declareProtected(ManagePortal, "needUpgrading")

    def needUpgrading(self) -> bool:
        # Need upgrading?
        return self.getInstanceVersion() != self.getFileSystemVersion()

    security.declareProtected(ManagePortal, "coreVersions")

    def coreVersions(self) -> VersionInformation:
        # Useful core information.
        plone_version = dist_version("Products.CMFPlone")
        instance_version = self.getInstanceVersion()
        fs_version = self.getFileSystemVersion()
        vars = {
            "Python": sys.version,
            "Zope": dist_version("Zope"),
            "Platform": sys.platform,
            "CMFPlone": plone_version,
            "Plone": plone_version,
            "Plone Instance": instance_version,
            "Plone File System": fs_version,
            "CMF": dist_version("Products.CMFCore"),
            "Debug mode": "Yes" if getConfiguration().debug_mode else "No",
            "PIL": _pil_version(),
            "core": {
                "name": self.friendly_name,
                "package_name": self.package_name,
                "package_version": self.getSoftwareVersion(),
                "instance_version": instance_version,
                "fs_version": fs_version,
            },
            "packages": {},
        }
        additional_packages = (
            "plone.classicui",
            "plone.distribution",
            "plone.exportimport",
            "plone.restapi",
            "plone.volto",
        )
        for package_name in additional_packages:
            try:
                vars["packages"][package_name] = dist_version(package_name)
            except PackageNotFoundError:
                pass
        return vars

    security.declareProtected(ManagePortal, "coreVersionsList")

    def coreVersionsList(self) -> list[str | dict | CoreVersionInformation]:
        # Useful core information.
        res = self.coreVersions().items()
        res.sort()
        return res

    security.declareProtected(ManagePortal, "needUpdateRole")

    def needUpdateRole(self) -> bool:
        # Do roles need to be updated?
        return bool(self._needUpdateRole)

    security.declareProtected(ManagePortal, "needRecatalog")

    def needRecatalog(self) -> bool:
        # Does this thing now need recataloging?
        return bool(self._needRecatalog)

    security.declareProtected(ManagePortal, "listUpgrades")

    def listUpgrades(self) -> list:
        # List available upgrade steps for our default profile.
        # Do not include upgrade steps for too new versions:
        # using a newer plone.app.upgrade version should not give problems.
        setup = self.setup
        fs_version = self.getFileSystemVersion()
        upgrades = setup.listUpgrades(self.profile, dest=fs_version)
        return upgrades

    security.declareProtected(ManagePortal, "list_steps")

    def list_steps(self) -> list:
        upgrades = self.listUpgrades()
        steps = []
        for u in upgrades:
            if isinstance(u, list):
                steps.extend(u)
            else:
                steps.append(u)
        return steps

    def _upgrade_run_steps(
        self, steps: list, logger: logging.Logger, swallow_errors: bool
    ) -> None:
        setup = self.setup
        for step in steps:
            try:
                step_title = step["title"]
                step["step"].doStep(setup)
                setup.setLastVersionForProfile(self.profile, step["dest"])
                logger.info(f"Ran upgrade step: {step_title}")
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

    def _upgrade_recatalog(self, logger: logging.Logger, swallow_errors: bool) -> None:
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
            logger.error(
                "Exception was thrown while cataloging:\n",
                exc_info=True,
            )
            if not swallow_errors:
                raise

    def _upgrade_roles(self, logger: logging.Logger, swallow_errors: bool) -> None:
        if self.needUpdateRole():
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

    security.declareProtected(ManagePortal, "upgrade")

    def upgrade(self, REQUEST=None, dry_run=None, swallow_errors=True) -> str:
        # This sets the profile version if it wasn't set yet
        version = self.getInstanceVersion()
        steps = self.list_steps()
        stream = StringIO()
        with get_logger(stream) as logger:
            if dry_run:
                logger.info("Dry run selected.")

            logger.info(f"Starting the migration from version: {version}")
            self._upgrade_run_steps(steps, logger, swallow_errors)
            logger.info("End of upgrade path, main migration has finished.")

            if self.needUpgrading():
                logger.error("The upgrade path did NOT reach current version.")
                logger.error("Migration has failed")
            else:
                logger.info("Starting upgrade of core addons.")
                self.addon_list.upgrade_all(self)
                logger.info("Done upgrading core addons.")

                # do this once all the changes have been done
                self._upgrade_recatalog(logger, swallow_errors=swallow_errors)
                self._upgrade_roles(logger, swallow_errors=swallow_errors)
                logger.info("Your Plone instance is now up-to-date.")

            if dry_run:
                logger.info("Dry run selected, transaction aborted")
                transaction.abort()

            return stream.getvalue()

    upgrade = postonly(upgrade)


def registerUpgradePath(oldversion, newversion, function):
    """Basic register func"""
    pass


InitializeClass(MigrationTool)
registerToolInterface("portal_migration", IMigrationTool)
