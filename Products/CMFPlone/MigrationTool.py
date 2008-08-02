import logging
import traceback
import sys

import transaction
from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, DevelopmentMode
from OFS.SimpleItem import SimpleItem
from ZODB.POSException import ConflictError

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFPlone.interfaces import IMigrationTool
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.utils import versionTupleFromString
from Products.CMFPlone.utils import log, log_deprecated
from AccessControl.requestmethod import postonly

_upgradePaths = {}
_widgetRegistry = {}

class MigrationTool(PloneBaseTool, UniqueObject, SimpleItem):
    """Handles migrations between Plone releases"""

    implements(IMigrationTool)

    id = 'portal_migration'
    meta_type = 'Plone Migration Tool'
    toolicon = 'skins/plone_images/site_icon.gif'

    __implements__ = (PloneBaseTool.__implements__, SimpleItem.__implements__, )

    _needRecatalog = 0
    _needUpdateRole = 0

    manage_options = (
        { 'label' : 'Upgrade', 'action' : 'manage_migrate' },
        )

    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'manage_overview')
    security.declareProtected(ManagePortal, 'manage_results')
    security.declareProtected(ManagePortal, 'manage_migrate')

    manage_migrate = DTMLFile('www/migrationRun', globals())
    manage_overview = DTMLFile('www/migrationTool', globals())
    manage_results = DTMLFile('www/migrationResults', globals())

    # Add a visual note
    def om_icons(self):
        icons = ({
                    'path':'misc_/CMFPlone/tool.gif',
                    'alt':self.meta_type,
                    'title':self.meta_type,
                 },)
        if self.needUpgrading() \
           or self.needUpdateRole() \
           or self.needRecatalog():
            icons = icons + ({
                     'path':'misc_/PageTemplates/exclamation.gif',
                     'alt':'Error',
                     'title':'This Plone instance needs updating'
                  },)

        return icons

    ##############################################################
    # Public methods
    #
    # versions methods

    security.declareProtected(ManagePortal, 'getInstanceVersion')
    def getInstanceVersion(self):
        """ The version this instance of plone is on """
        if getattr(self, '_version', None) is None:
            self.setInstanceVersion(self.getFileSystemVersion())
        return self._version.lower()

    security.declareProtected(ManagePortal, 'setInstanceVersion')
    def setInstanceVersion(self, version):
        """ The version this instance of plone is on """
        self._version = version

    security.declareProtected(ManagePortal, 'knownVersions')
    def knownVersions(self):
        """All known version ids, except current one and unsupported
           migration paths.
        """
        versions = [k for k in _upgradePaths if _upgradePaths[k][1] != False]
        return versions

    security.declareProtected(ManagePortal, 'unsupportedVersion')
    def unsupportedVersion(self):
        """Is the current instance version known to be a no longer supported
           version for migrations.
        """
        versions = [k for k in _upgradePaths if _upgradePaths[k][1] is False]
        return self._version in versions

    security.declareProtected(ManagePortal, 'getFileSystemVersion')
    def getFileSystemVersion(self):
        """ The version this instance of plone is on """
        return self.Control_Panel.Products.CMFPlone.version.lower()

    security.declareProtected(View, 'getFSVersionTuple')
    def getFSVersionTuple(self):
        """ returns tuple representing filesystem version """
        v_str = self.getFileSystemVersion()
        return versionTupleFromString(v_str)

    security.declareProtected(View, 'getInstanceVersionTuple')
    def getInstanceVersionTuple(self):
        """ returns tuple representing instance version """
        v_str = self.getInstanceVersion()
        return versionTupleFromString(v_str)

    security.declareProtected(ManagePortal, 'needUpgrading')
    def needUpgrading(self):
        """ Need upgrading? """
        return self.getInstanceVersion() != self.getFileSystemVersion()

    security.declareProtected(ManagePortal, 'coreVersions')
    def coreVersions(self):
        """ Useful core information """
        vars = {}
        cp = self.Control_Panel
        vars['Zope'] = cp.version_txt
        vars['Python'] = cp.sys_version
        vars['Platform'] = cp.sys_platform
        vars['Plone Instance'] = self.getInstanceVersion()
        vars['Plone File System'] = self.getFileSystemVersion()
        vars['CMF'] = cp.Products.CMFCore.version
        vars['Debug mode'] = DevelopmentMode and 'Yes' or 'No'
        try:
            from PIL.Image import VERSION
        except ImportError:
            VERSION = ''
        vars['PIL'] = VERSION
        return vars

    security.declareProtected(ManagePortal, 'coreVersionsList')
    def coreVersionsList(self):
        """ Useful core information """
        res = self.coreVersions().items()
        res.sort()
        return res

    security.declareProtected(ManagePortal, 'needUpdateRole')
    def needUpdateRole(self):
        """ Do roles need to be updated? """
        return self._needUpdateRole

    security.declareProtected(ManagePortal, 'needRecatalog')
    def needRecatalog(self):
        """ Does this thing now need recataloging? """
        return self._needRecatalog

    security.declareProtected(ManagePortal,'getProductInfo')
    def getProductInfo(self):
        """Provide information about installed products for error reporting"""
        zope_products = self.getPhysicalRoot().Control_Panel.Products.objectValues()
        installed_products = getToolByName(self, 'portal_quickinstaller').listInstalledProducts(showHidden=1)
        products = {}
        for p in zope_products:
            product_info = {'id':p.id, 'version':p.version}
            for ip in installed_products:
                if ip['id'] == p.id:
                    product_info['status'] = ip['status']
                    product_info['hasError'] = ip['hasError']
                    product_info['installedVersion'] = ip['installedVersion']
                    break
            products[p.id] = product_info
        return products

    security.declareProtected(ManagePortal,'getPILVersion')
    def getPILVersion(self):
        """The version of the installed Python Imaging Library."""
        log_deprecated("getPILVersion is deprecated and will be removed in "
                       "Plone 4.0. Please use coreVersions instead.")
        try:
            from PIL.Image import VERSION
        except ImportError:
            VERSION = None
        return VERSION

    security.declareProtected(ManagePortal, 'upgrade')
    def upgrade(self, REQUEST=None, dry_run=None, swallow_errors=1):
        """ perform the upgrade """
        # keep it simple
        out = []

        self._check()

        if dry_run:
            out.append(("Dry run selected.", logging.INFO))

        # either get the forced upgrade instance or the current instance
        newv = getattr(REQUEST, "force_instance_version",
                       self.getInstanceVersion())

        out.append(("Starting the migration from "
                    "version: %s" % newv, logging.INFO))
        while newv is not None:
            out.append(("Attempting to upgrade from: %s" % newv, logging.INFO))
            try:
                newv, msgs = self._upgrade(newv)
                if msgs:
                    for msg in msgs:
                        # if string make list
                        if isinstance(msg, basestring):
                            msg = [msg,]
                        # if no status, add one
                        if len(msg) == 1:
                            msg.append(logging.INFO)
                        out.append(msg)
                if newv is not None:
                    out.append(("Upgrade to: %s, completed" % newv, logging.INFO))
                    self.setInstanceVersion(newv)

            except ConflictError:
                raise
            except:
                out.append(("Upgrade aborted", logging.ERROR))
                out.append(("Error type: %s" % sys.exc_type, logging.ERROR))
                out.append(("Error value: %s" % sys.exc_value, logging.ERROR))
                for line in traceback.format_tb(sys.exc_traceback):
                    out.append((line, logging.ERROR))

                # set newv to None
                # to break the loop
                newv = None
                if not swallow_errors:
                    for msg, sev in out: log(msg, severity=sev)
                    raise
                else:
                    # abort transaction to safe the zodb
                    transaction.abort()

        out.append(("End of upgrade path, migration has finished", logging.INFO))

        if self.needUpgrading():
            out.append((("The upgrade path did NOT reach "
                        "current version"), logging.ERROR))
            out.append(("Migration has failed", logging.ERROR))
        else:
            out.append((("Your ZODB and Filesystem Plone "
                         "instances are now up-to-date."), logging.INFO))

        # do this once all the changes have been done
        if self.needRecatalog():
            try:
                catalog = self.portal_catalog
                # Reduce threshold for the reindex run
                old_threshold = catalog.threshold
                pg_threshold = getattr(catalog, 'pgthreshold', 0)
                catalog.pgthreshold = 300
                catalog.threshold = 2000
                catalog.refreshCatalog(clear=1)
                catalog.threshold = old_threshold
                catalog.pgthreshold = pg_threshold
                self._needRecatalog = 0
            except ConflictError:
                raise
            except:
                out.append(("Exception was thrown while cataloging",
                            logging.ERROR))
                for line in traceback.format_tb(sys.exc_traceback):
                    out.append((line, logging.ERROR))
                if not swallow_errors:
                    for msg, sev in out: log(msg, severity=sev)
                    raise

        if self.needUpdateRole():
            try:
                self.portal_workflow.updateRoleMappings()
                self._needUpdateRole = 0
            except ConflictError:
                raise
            except:
                out.append((("Exception was thrown while updating "
                             "role mappings"), logging.ERROR))
                for line in traceback.format_tb(sys.exc_traceback):
                    out.append((line, logging.ERROR))
                if not swallow_errors:
                    for msg, sev in out: log(msg, severity=sev)
                    raise

        if dry_run:
            out.append(("Dry run selected, transaction aborted", logging.INFO))
            transaction.abort()

        # log all this
        for msg, sev in out: log(msg, severity=sev)
        try:
            return self.manage_results(self, out=out)
        except NameError:
            pass
    upgrade = postonly(upgrade)

    ##############################################################
    # Private methods

    def _check(self):
        """ Are we inside a Plone site?  Are we allowed? """
        if getattr(self,'portal_url', []) == []:
            raise AttributeError, 'You must be in a Plone site to migrate.'

    def _upgrade(self, version):
        version = version.lower()
        if not _upgradePaths.has_key(version):
            return None, ("Migration completed at version %s." % version,)

        newversion, function = _upgradePaths[version]
        # This means a now unsupported migration path has been triggered
        if function is False:
            return None, ("Migration stopped at version %s." % version,)
        res = function(self.aq_parent)
        return newversion, res

def registerUpgradePath(oldversion, newversion, function):
    """ Basic register func """
    _upgradePaths[oldversion.lower()] = [newversion.lower(), function]

InitializeClass(MigrationTool)
registerToolInterface('portal_migration', IMigrationTool)
