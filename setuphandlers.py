"""
CMFPlone setup handlers.
"""

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions as cmfpermissions

class PloneGenerator:
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

    def setupNavTree(self,p):
        ''' sets up the default propertysheet for the navtree '''
        # XXX make the portal_properties handler smarter so this
        #     is all fed from the XML
        prop_tool = getToolByName(p, 'portal_properties')
        prop_tool.manage_addPropertySheet('navtree_properties',
                                          'NavigationTree properties')

        ntp=prop_tool.navtree_properties
        navtree_bl=['ATBooleanCriterion',
                    'ATCurrentAuthorCriterion',
                    'ATPathCriterion',
                    'ATDateCriteria',
                    'ATDateRangeCriterion',
                    'ATListCriterion',
                    'ATPortalTypeCriterion',
                    'ATReferenceCriterion',
                    'ATSelectionCriterion',
                    'ATSimpleIntCriterion',
                    'ATSimpleStringCriterion',
                    'ATSortCriterion',
                    'Discussion Item',
                    'Plone Site',
                    'TempFolder']
        ntp._setProperty('typesNotToList', navtree_bl, 'lines')
        ntp._setProperty('sortAttribute', 'getObjPositionInParent', 'string')
        ntp._setProperty('sortOrder', 'asc', 'string')
        ntp._setProperty('sitemapDepth', 3, 'int')
        ntp._setProperty('includeTop', 1, 'boolean')

        # TODO: needs to be supported
        ntp._setProperty('topLevel', 0, 'int')
        ntp._setProperty('idsNotToList', [] , 'lines')
        ntp._setProperty('skipIndex_html',1,'boolean')
        ntp._setProperty('showAllParents',1,'boolean')

        # Canditates to be implemented
        ntp._setProperty('showMyUserFolderOnly', 1, 'boolean')
        ntp._setProperty('showFolderishSiblingsOnly', 1, 'boolean')
        ntp._setProperty('showFolderishChildrenOnly', 1, 'boolean')
        ntp._setProperty('showNonFolderishObject', 0, 'boolean')
        ntp._setProperty('showTopicResults', 1, 'boolean')
        ntp._setProperty('rolesSeeUnpublishedContent', ['Manager','Reviewer','Owner'] , 'lines')
        ntp._setProperty('sortCriteria', ['isPrincipiaFolderish,desc']  , 'lines')
        ntp._setProperty('parentMetaTypesNotToQuery',['TempFolder'],'lines')

        # The following properties will not be supported anymore         
        ntp._setProperty('batchSize', 30, 'int')
        ntp._setProperty('croppingLength',256,'int')
        ntp._setProperty('forceParentsInBatch',0,'boolean')
        ntp._setProperty('rolesSeeContentsView', ['Manager','Reviewer','Owner'] , 'lines')
        ntp._setProperty('rolesSeeHiddenContent', ['Manager',] , 'lines')
        ntp._setProperty('bottomLevel', 65535 , 'int')


def importVarious(context):
    """
    Import various settings.

    Provisional handler that does initialization that is not yet taken
    care of by other handlers.
    """
    gen = PloneGenerator()
    p = getToolByName(context, 'portal_url').getPortalObject()
    gen.customizePortalOptions(p)
    gen.setupPortalContent(p)
    gen.setupNavTree(p)
