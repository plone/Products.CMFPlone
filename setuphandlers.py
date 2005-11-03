"""
CMFPlone setup handlers.
"""

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions as cmfpermissions

class PloneGenerator:

    def installProducts(self, p):
        """QuickInstaller install of required Products"""
        # XXX These should all be done via a CMFSetup handler
        qi = getToolByName(p, 'portal_quickinstaller')
        qi.installProduct('Archetypes', locked=1)
        qi.installProduct('CMFFormController', locked=1)
        qi.installProduct('GroupUserFolder', locked=1)
        #qi.installProduct('ATContentTypes', locked=1)


    def customizePortalOptions(self, p):
        p.manage_permission( cmfpermissions.ListFolderContents, \
                             ('Manager', 'Member', 'Owner',), acquire=1 )
        stool = getToolByName(p, 'portal_skins')
        stool.allow_any=0 # Skin changing for users is turned off by default
        #p.icon = 'misc_/CMFPlone/plone_icon'

    def setupPortalContent(self, p):
        # add Members folder
        p.invokeFactory('Large Plone Folder', 'Members')
        members = getattr(p , 'Members')
        members.setTitle('Members')
        members.setDescription("Container for portal members' home directories")

        # add front page to portal root
        p.invokeFactory('Document', 'front-page')
        idx = getattr(p, 'front-page')
        idx.setTitle('Welcome to Plone')
        idx.setDescription('Congratulations! You have successfully'+\
                         ' installed Plone.')
        idx.setFormat('html')
        if idx.meta_type == 'Document':
            # CMFDefault document
            idx.edit('html', default_frontpage)
        else:
            idx.edit(text=default_frontpage)
        idx.reindexObject()

        p.setDefaultPage('front-page')

        # add index_html to Members area
        addPy = members.manage_addProduct['PythonScripts'].manage_addPythonScript
        addPy('index_html')
        index_html = getattr(members, 'index_html')
        index_html.write(member_indexhtml)
        index_html.ZPythonScript_setTitle('Member Search')

def importVarious(context):
    """
    Import various settings.

    Provisional handler that does initialization that is not yet taken
    care of by other handlers.
    """
    site = context.getSite()

    gen = PloneGenerator()

    gen.installProducts(site)
    gen.customizePortalOptions(site)
    #gen.setupPortalContent(site)
