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
    manage_overview = DTMLFile('www/migrationTool', globals())

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

    security.declareProtected(ManagePortal, 'knownVersions')
    def knownVersions(self):
        """ All known version ids, except current one """
        return _upgradePaths.keys()

    security.declareProtected(ManagePortal, 'getFileSystemVersion')
    def getFileSystemVersion(self):
        """ The version this instance of plone is on """
        return self.Control_Panel.Products.CMFPlone.version

    security.declareProtected(ManagePortal, 'needUpgrading')
    def needUpgrading(self):
        """ Need upgrading? """
        return self.getInstanceVersion() != self.getFileSystemVersion()

    security.declareProtected(ManagePortal, 'upgrade')
    def upgrade(self, REQUEST=None):
        """ perform the upgrade """
        if REQUEST is None:
            REQUEST = self.REQUEST
        out = REQUEST.RESPONSE
        if out is None:
            # FIXME - perhaps zLOG?
            import StringIO
            out = StringIO.StringIO()
        newv = None
        if getattr(REQUEST, 'yes_I_am_very_sure', None):
            newv = REQUEST.get("force_instance_version", None)
        if newv is None:
            newv = self.getInstanceVersion()
        while newv is not None:
            out.write('upgrading from ' + repr(newv))
            try:
                newv = self._upgrade(newv)
            except:
                import traceback
                out.write(' - ERROR!\n')
                traceback.print_exc(file=out)
                raise
            if newv is not None:
                out.write(' to %s: ok\n' % repr(newv))
            self.setInstanceVersion(newv)
        out.write(' - hit end of upgrade path\n')
        
        if self.needUpgrading():
            out.write('PROBLEM: upgrade path did NOT reach current version\nMIGRATION FAILED')
        else:
            out.write('ok, this is the current version.\nMigration completed successfuly')

        # do this once all the changes have been done
        self.portal_catalog.refreshCatalog()
        self.portal_workflow.updateRoleMappings()
        

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
