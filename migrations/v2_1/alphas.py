import os

from Acquisition import aq_base
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct


def two05_alpha1(portal):
    """2.0.5 -> 2.1-alpha1
    """
    out = []
    
    # ATCT is not installed when SUPPRESS_ATCT_INSTALLATION is set to YES
    # It's required for some unit tests in ATCT [tiran]
    suppress_atct = bool(os.environ.get('SUPPRESS_ATCT_INSTALLATION', None)
                         == 'YES')

    # Install SecureMailHost
    replaceMailHost(portal, out)

    # Remove legacy tools
    deleteTool(portal, out, 'portal_form')
    deleteTool(portal, out, 'portal_navigation')

    # Remove old properties
    deletePropertySheet(portal, out, 'form_properties')
    deletePropertySheet(portal, out, 'navigation_properties')

    # Install Archetypes
    installArchetypes(portal, out)
    
    # install ATContentTypes
    if not suppress_atct:
        installATContentTypes(portal, out)

        # XXX: Hack
        patchATCTMigration()

        # Switch over to ATCT
        migrateToATCT(portal, out)

    return out

def alpha1_alpha2(portal):
    """2.1-alpha1 -> 2.1-alpha2
    """
    out =[]
    ntp = portal.portal_properties.navtree_properties
    # Plone Setup has changed because of the new Nav Tree implementation
    # StatelessTreeNav had a createNavTreePropertySheet method which is now
    # in Portal.py (including the new properties)
    # If typesTolist is not there were dealing with a real migration
    if not ntp.hasProperty('typesToList'):
        ntp._setProperty('typesToList', ['Folder'], 'lines')
        ntp._setProperty('sortAttribute', 'getFolderOrder', 'string')
        ntp._setProperty('sortOrder', 'asc', 'string')
        ntp._setProperty('sitemapDepth', 3, 'int')
    out.append('Updated properties to navtree')
            
    #replace path index with ExtendedPathIndex
    ct = portal.portal_catalog
    ct.delIndex('path')
    ct.addIndex('path', 'ExtendedPathIndex')
    out.append('Replaced path index')
    
    # Add indexes
    if 'getFolderOrder' not in ct.indexes():
        ct.addIndex('getFolderOrder', 'FieldIndex')
    if 'isDefaultPage' not in ct.indexes():
        ct.addIndex('isDefaultPage', 'FieldIndex')
    out.append('Added indexes')
    
    # Refresh skins to make the getFolderOrder available to catalog
    if hasattr(portal, '_v_skindata'):
        portal._v_skindata = None
    if hasattr(portal, 'setupCurrentSkin'):
        portal.setupCurrentSkin()

    ct.refreshCatalog(clear=1)
    
    at = portal.portal_actions
    at.addAction('sitemap',
                 'Sitemap',
                 'string:$portal_url/sitemap',
                 '', #condition
                 View,
                 'site_actions')
    out.append('Added Sitemap action')

    return out

def replaceMailHost(portal, out):
    """Replaces the mailhost with a secure mail host."""
    id = 'MailHost'
    oldmh = getattr(aq_base(portal), id)
    if oldmh.meta_type == 'Secure Mail Host':
        out.append('Secure Mail Host already installed')
        return
    title = oldmh.title
    smtp_host = oldmh.smtp_host
    smtp_port = oldmh.smtp_port
    portal.manage_delObjects([id])
    out.append('Removed old MailHost')

    addMailhost = portal.manage_addProduct['SecureMailHost'].manage_addMailHost
    addMailhost(id, title=title, smtp_host=smtp_host, smtp_port=smtp_port)
    out.append('Added new MailHost (SecureMailHost): %s:%s' % (smtp_host, smtp_port))


def deleteTool(portal, out, tool_name):
    """Deletes a tool."""
    if hasattr(aq_base(portal), tool_name):
        portal._delObject(tool_name)
    out.append('Deleted %s tool.' % tool_name)


def deletePropertySheet(portal, out, sheet_name):
    """Deletes a property sheet from portal_properties."""
    proptool = portal.portal_properties
    if hasattr(aq_base(proptool), sheet_name):
        proptool._delObject(sheet_name)
    out.append('Deleted %s property sheet.' % sheet_name)


def installArchetypes(portal, out):
    """Quickinstalls Archetypes if not installed yet."""
    for product_name in ('MimetypesRegistry', 'PortalTransforms', 'Archetypes'):
        installOrReinstallProduct(portal, product_name, out)


def installATContentTypes(portal, out):
    """Quickinstalls ATContentTypes if not installed yet."""
    for product_name in ('ATContentTypes',):
        installOrReinstallProduct(portal, product_name, out)


def migrateToATCT(portal, out):
    """Switches portal to ATContentTypes."""
    get_transaction().commit(1)
    migrateFromCMFtoATCT = portal.migrateFromCMFtoATCT
    switchCMF2ATCT = portal.switchCMF2ATCT
    #out.append('Migrating and switching to ATContentTypes ...')
    result = migrateFromCMFtoATCT()
    out.append(result)
    try:
        switchCMF2ATCT(skip_rename=False)
    except IndexError:
        switchCMF2ATCT(skip_rename=True)
    get_transaction().commit(1)
    #out.append('Switched portal to ATContentTypes.')


# XXX: Hack! Will go away once ATCT 1.0 is ready
try:

    from Products.ATContentTypes.migration.common import unrestricted_rename
    def patchATCTMigration(): pass

except ImportError:
    # ATCT 0.2

    # Temporarily cribbed from ATCT 1.0. Thanks Tiran ;-)
    def unrestricted_rename(self, id, new_id):
        """Rename a particular sub-object

        Copied from OFS.CopySupport

        Less strict version of manage_renameObject:
            * no write lock check
            * no verify object check from PortalFolder so it's allowed to rename
              even unallowed portal types inside a folder
        """
        try: self._checkId(new_id)
        except: raise CopyError, MessageDialog(
                      title='Invalid Id',
                      message=sys.exc_info()[1],
                      action ='manage_main')
        ob=self._getOb(id)
        #!#if ob.wl_isLocked():
        #!#    raise ResourceLockedError, 'Object "%s" is locked via WebDAV' % ob.getId()
        if not ob.cb_isMoveable():
            raise CopyError, eNotSupported % escape(id)
        #!#self._verifyObjectPaste(ob)
        #!#CopyContainer._verifyObjectPaste(self, ob)
        try:    ob._notifyOfCopyTo(self, op=1)
        except: raise CopyError, MessageDialog(
                      title='Rename Error',
                      message=sys.exc_info()[1],
                      action ='manage_main')
        self._delObject(id)
        ob = aq_base(ob)
        ob._setId(new_id)

        # Note - because a rename always keeps the same context, we
        # can just leave the ownership info unchanged.
        self._setObject(new_id, ob, set_owner=0)
        ob = self._getOb(new_id)
        ob._postCopy(self, op=1)

        #!#if REQUEST is not None:
        #!#    return self.manage_main(self, REQUEST, update_menu=1)
        return None

    def patchATCTMigration():
        def renameOld(self):
            unrestricted_rename(self.parent, self.orig_id, self.old_id)
        from Products.ATContentTypes.migration.Migrator import ItemMigrationMixin
        ItemMigrationMixin.renameOld = renameOld

