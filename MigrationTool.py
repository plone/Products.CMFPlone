from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.CMFCorePermissions import ManagePortal

import zLOG
import traceback
import sys

def log(message,summary='',severity=0):
    zLOG.LOG('Plone: ',severity,summary,message)

_upgradePaths = {}

class MigrationTool( UniqueObject, SimpleItem):
    id = 'portal_migration'
    meta_type = 'Plone Migration Tool'

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }, )

    security = ClassSecurityInfo()
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('www/migrationTool', globals())

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
        """ All known version ids, except current one """
        return _upgradePaths.keys()

    security.declareProtected(ManagePortal, 'getFileSystemVersion')
    def getFileSystemVersion(self):
        """ The version this instance of plone is on """
        return self.Control_Panel.Products.CMFPlone.version.lower()

    security.declareProtected(ManagePortal, 'needUpgrading')
    def needUpgrading(self):
        """ Need upgrading? """
        return self.getInstanceVersion() != self.getFileSystemVersion()

    def _check(self):
        """ Are we inside a Plone site?  Are we allowed? """
        if not hasattr(self,'portal_url'):
            raise 'You must be in a Plone site to migrate.'
        
    security.declareProtected(ManagePortal, 'upgrade')
    def upgrade(self, REQUEST=None, dry_run=None):
        """ perform the upgrade """
        # keep it simple
        out = []

        self._check()
        
        # either get the forced upgrade instance or the current instance
        newv = getattr(REQUEST, "force_instance_version", self.getInstanceVersion())
       
        out.append("Starting the migration from version: %s" % newv)
        while newv is not None:
            out.append("Attempting to upgrade from: %s" % newv)
            try:
                newv = self._upgrade(newv)
                if newv is not None:
                    out.append("Upgrade to: %s, completed" % newv)
                    self.setInstanceVersion(newv)
                else:
                    out.append("No upgrade path found from that version, migration stopping")
            except:
                out.append('ERROR:')
                out += traceback.format_tb(sys.exc_traceback)
                out.append("Upgrade aborted")
                # set newv to None
                # to break the loop
                newv = None
                
        out.append("End of upgrade path, migration has finished")
        
        if self.needUpgrading():
            out.append("PROBLEM: The upgrade path did NOT reach current version")
            out.append("Migration has failed")

        # do this once all the changes have been done
        try:
            self.portal_catalog.refreshCatalog()
            self.portal_workflow.updateRoleMappings()
        except:
            out.append("Exception was thrown while cataloging and updating role mappings")
            out += traceback.format_tb(sys.exc_traceback)

        if dry_run:
            out.append("Dry run selected, transaction aborted")
            get_transaction().abort()
            
        return '\n'.join(out)
        

    def _upgrade(self, version):
        version = version.lower()
        if not _upgradePaths.has_key(version): 
            #log('No upgrade path found for version "%s"\n' % version)
            return None

        newversion, function = _upgradePaths[version]
        function(self.aq_parent)
        return newversion


def registerUpgradePath(oldversion, newversion, function): 
    """ Basic register func """
    _upgradePaths[oldversion.lower()] = [newversion.lower(), function]

InitializeClass(MigrationTool)
