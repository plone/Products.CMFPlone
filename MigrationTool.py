from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.CMFCorePermissions import ManagePortal

import zLOG

def log(message,summary='',severity=0):
    zLOG.LOG('Plone: ',severity,summary,message)

_upgradePaths = {}

class MigrationTool( UniqueObject, SimpleItem):
    id = 'portal_migration'
    meta_type = 'Plone Migration Tool'

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }, )

    security = ClassSecurityInfo()
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('tool_forms/migrationTool', globals())

    security.declareProtected(ManagePortal, 'getInstanceVersion')
    def getInstanceVersion(self):
        """ The version this instance of plone is on """
        if getattr(self, '_version', None) is None:
            self.setInstanceVersion(self.getFileSystemVersion())
        return self._version

    security.declareProtected(ManagePortal, 'setInstanceVersion')
    def setInstanceVersion(self, version):
        """ The version this instance of plone is on """
        self._version = version

    security.declareProtected(ManagePortal, 'getFileSystemVersion')
    def getFileSystemVersion(self):
        """ The version this instance of plone is on """
        return self.Control_Panel.Products.CMFPlone.version

    security.declareProtected(ManagePortal, 'setInstanceVersion')
    def needUpgrading(self):
        """ Need upgrading? """
        return self.getInstanceVersion() != self.getFileSystemVersion()

    security.declareProtected(ManagePortal, 'upgrade')
    def upgrade(self, REQUEST=None):
        """ perform the upgrade """
        newv = self.getInstanceVersion()
        while newv is not None:
            newv = self._upgrade(newv)
            self.setInstanceVersion(newv)

        # do this once all the changes have been done
        self.portal_catalog.refreshCatalog()
        self.portal_workflow.updateRoleMappings()
        
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('manage_main')

    def _upgrade(self, version):
        if not _upgradePaths.has_key(version): 
            log('No upgrade path found for version "%s"' % version)
            return None

        newversion, function = _upgradePaths[version]
        function(self.aq_parent)
        return newversion

def registerUpgradePath(oldversion, newversion, function): 
    """ Basic register func """
    _upgradePaths[oldversion] = [newversion, function]

InitializeClass(MigrationTool)
