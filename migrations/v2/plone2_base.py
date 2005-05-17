# this is the Plone 2.0 base setup

#inlined and tidy of all the things that make a plone
#different from stock CMF, portal.

#When this is done the follow migrations can be tossed:
# beta2_beta3
# beta3_rc1
# rc1_rc2
# rc2_final
# final_one_zero_one
# one01_one02
# one02_one03
# upg_1_0_1_to_1_1

from cStringIO import StringIO
from Acquisition import aq_base

from Products.StandardCacheManagers import AcceleratedHTTPCacheManager, RAMCacheManager
from Products.CMFCore.TypesTool import ContentFactoryMetadata, FactoryTypeInformation

from Products.CMFDefault.Document import addDocument
from Globals import package_home
from Products.CMFPlone import cmfplone_globals
from Products.CMFQuickInstallerTool import QuickInstallerTool, AlreadyInstalled
from Products.CMFPlone.setup.ConfigurationMethods import addSiteProperties
from Products.CMFPlone.migrations.migration_util import safeEditProperty
from Products.CMFPlone import ToolNames

from Products.CMFCore import CachingPolicyManager
from Products.CMFCore.CMFCorePermissions import ListFolderContents, SetOwnProperties, SetOwnPassword
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.TypesTool import FactoryTypeInformation
from ZODB.POSException import ConflictError

def make_plone(portal):
    typesTool = portal.portal_types
    wf_tool=portal.portal_workflow
    folder_wf = wf_tool['folder_workflow']
    folder_wf.states.visible.permission_roles[ListFolderContents]=('Manager', 'Owner', 'Member')

    #addPortalFormValidators(portal)    # Gone since 2.1
    addCatalogIndexes(portal)
    addCatalogLexicon(portal)
    addSiteProperties(portal,portal)
    #addNavigationProperties(portal)    # Gone since 2.1
    extendSiteProperties(portal)
    extendMemberdata(portal)
    addDefaultPloneSkins(portal)
    setupDefaultEditor(portal)
    setupCalendar(portal)

    #1.0.1->1.0.3
    cookie_authentication = getToolByName(portal, 'cookie_authentication')
    cookie_authentication._updateProperty('auto_login_page', 'require_login')

    #1.0.2->1.0.3
    site_props=portal.portal_properties.site_properties
    safeEditProperty(site_props,'invalid_ids',('actions',),'lines')

    #1.1 Configuration
    #This is used by PloneFolders to pick the default object to render
    #used by browserDefault and is similiar to index files in apache
    default_pages = ['index_html', 'index.html', 'index.htm', 'FrontPage']
    safeEditProperty(site_props,'default_page',default_pages,'lines')

    #Support for cropping descriptions in search results
    safeEditProperty(site_props,'search_results_description_length',160,'int')
    safeEditProperty(site_props,'ellipsis','...','string')

    #We depend on CMFQuickInstaller
    if 'portal_quickinstaller' not in portal.objectIds():
        portal.manage_addProduct['CMFPlone'].manage_addTool(ToolNames.QuickInstallerTool)

    addGroupUserFolder(portal)
    portal.portal_syndication.isAllowed = 0
    addDocumentActions(portal)
    addActionIcons(portal)
    addCacheAccelerators(portal)
    #XXX TODO:migrate to add simple workflow
    # change the action in portal_types for viewing a folder
    if 'portal_interface' not in portal.objectIds():
        manage_addTool=portal.manage_addProduct['CMFPlone'].manage_addTool
        manage_addTool(ToolNames.InterfaceTool)
    addControlPanel(portal)
    upgradePortalFactory(portal)

    #Add State tabs to portal_types individually instead of globally
    addActionsToPortalTypes(portal)

    #Add Form Controller - yay for features!
    addFormController(portal)

    #Set a portal_type on the root Plone Site
    makePortalRootPortalType(portal)

    #Set ext_editor property in site_properties
    setupExtEditor(portal)

def addFormController(portal):
    qi=getToolByName(portal,'portal_quickinstaller')
    qi.installProduct('CMFFormController',locked=1)

def addPortalFormValidators(portal):
    form_tool = portal.portal_form
    form_tool.setValidators('folder_rename_form', ['validate_folder_rename'])
    form_tool.setValidators('sendto_form', ['validate_sendto'])
    #1.0->1.0.1
    form_tool.setValidators('synPropertiesForm', ['validate_synPropertiesForm'])

def addCatalogIndexes(portal):
    catalog = portal.portal_catalog
    if not catalog._catalog.schema.has_key('getId'):
        catalog.addColumn('getId', None)
    if not catalog._catalog.schema.has_key('meta_type'):
        catalog.addColumn('meta_type', None)
    if not catalog._catalog.schema.has_key('location'):
        catalog.addColumn('location', None)
    if not catalog._catalog.schema.has_key('getRemoteUrl'):
        catalog.addColumn('getRemoteUrl', None)

def addCatalogLexicon(portal):
    from OFS.ObjectManager import BadRequestException
    catalog = portal.portal_catalog

    class largs:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    try:
        catalog.manage_addProduct[ 'ZCTextIndex' ].manage_addLexicon(
            'plone_lexicon',
            elements=[
            largs(group= 'Case Normalizer' , name= 'Case Normalizer' ),
            largs(group= 'Stop Words', name= " Don't remove stop words" ),
            largs(group= 'Word Splitter' , name= "Unicode Whitespace splitter" ),
            ]
            )
    except BadRequestException:
        # lexicon id already in use
        pass

def addNavigationProperties(portal):
    nav_tool=portal.portal_navigation
    nav_tool.addTransitionFor('default','createObject','success','action:edit')
    nav_tool.addTransitionFor('default','sendto_form','success','script:sendto')
    nav_tool.addTransitionFor('default','sendto_form','failure','sendto_form')
    nav_tool.addTransitionFor('default','sendto','success','action:view')
    nav_tool.addTransitionFor('default','sendto','failure','action:view')
    # these were missed in the initial beta 3 release
    nav_tool.addTransitionFor('default','folder_rename_form','failure','folder_rename_form')
    nav_tool.addTransitionFor('default','folder_rename_form','success','script:folder_rename')
    nav_tool.addTransitionFor('default','register','failure','join_form')
    #rc2-1.0
    nav_tool.addTransitionFor('default','content_status_modify','failure','content_status_history')
    #1.0->1.0.1
    nav_tool.addTransitionFor('default','synPropertiesForm','success','script:editSynProperties')
    nav_tool.addTransitionFor('default','synPropertiesForm','failure','synPropertiesForm')
    nav_tool.addTransitionFor('default','editSynProperties','success','url:folder_contents')
    nav_tool.addTransitionFor('default','editSynProperties','failure','synPropertiesForm')
    #1.1
    nav_tool.addTransitionFor('default','reconfig','success','url:plone_control_panel')

def extendSiteProperties(portal):
    #beta3-rc1
    props = portal.portal_properties.site_properties
    if not hasattr(props, 'allowRolesToAddKeywords'):
        props._setProperty('allowRolesToAddKeywords', ['Manager', 'Reviewer'], 'lines')

def extendMemberdata(portal):
    if not portal.portal_memberdata.hasProperty('fullname'):
        portal.portal_memberdata.manage_addProperty('fullname', '', 'string')
    if not portal.portal_memberdata.hasProperty('error_log_update'):
        portal.portal_memberdata.manage_addProperty('error_log_update', 0.0, 'float')

def addDefaultPloneSkins(portal):
    pass

# XXX I assume these can be removed, since they no longer ship with Plone.
#
#    from Products.CMFPlone.Portal import PloneGenerator
#    pg=PloneGenerator()
#    sk_tool=getToolByName(portal, 'portal_skins')
#
#    setup_skins=pg.setupSecondarySkin
#    setup_skins(sk_tool, 'Plone Core',          'plone_styles/core')
#    setup_skins(sk_tool, 'Plone Corporate',     'plone_styles/corporate')
#    setup_skins(sk_tool, 'Plone Autumn',        'plone_styles/autumn')
#    setup_skins(sk_tool, 'Plone Core Inverted', 'plone_styles/core_inverted')
#    setup_skins(sk_tool, 'Plone Greensleeves',  'plone_styles/greensleeves')
#    setup_skins(sk_tool, 'Plone Kitty',         'plone_styles/kitty')
#    setup_skins(sk_tool, 'Plone Mozilla New',   'plone_styles/mozilla_new')
#    setup_skins(sk_tool, 'Plone Prime',         'plone_styles/prime')
#    setup_skins(sk_tool, 'Plone Zed',           'plone_styles/zed')

def setupDefaultEditor(portal):
    pass

def addGroupUserFolder(portal):
    """ We _must_ commit() here.  Because the Portal does not really exist in
        the ZODB.  And the acl_users object we are moving *must* have a _p_jar
        attribute.  We get the Connection object by commit()ing.

        NOTE: In the Install routine for GRUF it does a subtransaction commit()
        so that you can manipulate the acl_users folders.
    """
    get_transaction().commit(1)
    out=[]
    out.append('Adding GroupUserFolder to portal')
    qi=getToolByName(portal, 'portal_quickinstaller')
    qi.installProduct('GroupUserFolder',locked=1)
    addPloneTool=portal.manage_addProduct['CMFPlone'].manage_addTool
    portal_ids = aq_base(portal).objectIds()
    if 'portal_groups' not in portal_ids:
        out.append('Adding portal_groups tool to portal')
        addPloneTool(ToolNames.GroupsTool)
    if 'portal_groupdata' not in portal_ids:
        out.append('Adding portal_groupdata tool to portal')
        addPloneTool(ToolNames.GroupDataTool)
    return out

def addDocumentActions(portal):
    at = portal.portal_actions

    at.addAction('extedit',
                 'Edit this file in an external application (Requires Zope ExternalEditor installed)',
                 'string:$object_url/external_edit',
                 "python: hasattr(portal.portal_properties.site_properties, 'ext_editor') and portal.portal_properties.site_properties.ext_editor and object.absolute_url() != portal_url",
                 'Modify portal content',
                 'document_actions')

    at.addAction('rss',
                 'RSS feed of this folder\'s contents',
                 'string:$object_url/RSS',
                 'python:portal.portal_syndication.isSyndicationAllowed(object)',
                 'View',
                 'document_actions')

    at.addAction('sendto',
                 'Send this page to somebody',
                 'string:$object_url/sendto_form',
                 '',
                 'View',
                 'document_actions')

    at.addAction('print',
                 'Print this page',
                 'string:javascript:this.print();',
                 '',
                 'View',
                 'document_actions')

    at.addAction('addtofavorites',
                 'Add to Favorites',
                 'string:${object_url}/addtoFavorites',
                 'python: member and portal.portal_membership.getHomeFolder()',
                 'View',
                 'document_actions',
                 visible=0)


def upgradePortalFactory(portal):
    typesTool = getToolByName(portal, 'portal_types')
    # add temporary folder type for portal_factory
    if not hasattr(typesTool, 'TempFolder'):
        typesTool.manage_addTypeInformation(FactoryTypeInformation.meta_type,
                                             id='TempFolder',
                                             typeinfo_name='CMFCore: Portal Folder')
        folder = typesTool.Folder
        tempfolder = typesTool.TempFolder
        tempfolder.content_meta_type='TempFolder'
        tempfolder.icon = folder.icon
        tempfolder.global_allow = 0  # make TempFolder not implicitly addable
        tempfolder.allowed_content_types=(typesTool.listContentTypes())

def addControlPanel(portal):
    from Products.CMFPlone.ToolNames import ControlPanelTool
    addPloneTool=portal.manage_addProduct['CMFPlone'].manage_addTool
    if not hasattr(portal.aq_explicit,'portal_controlpanel'):
        addPloneTool(ControlPanelTool, None)
    # must be done here because controlpanel depends on
    # portal_actionicons concerning icon registration
    portal.portal_controlpanel.registerDefaultConfiglets()


def addCacheAccelerators(portal):
    # add in caches, HTTPCache and RamCache
    meta_type = AcceleratedHTTPCacheManager.AcceleratedHTTPCacheManager.meta_type
    if 'HTTPCache' not in portal.objectIds(meta_type):
        AcceleratedHTTPCacheManager.manage_addAcceleratedHTTPCacheManager(portal, 'HTTPCache')
    meta_type = RAMCacheManager.RAMCacheManager.meta_type
    if 'RAMCache' not in portal.objectIds(meta_type):
        RAMCacheManager.manage_addRAMCacheManager(portal, 'RAMCache')
    if 'caching_policy_manager' not in portal.objectIds():
        CachingPolicyManager.manage_addCachingPolicyManager(portal)

def setupHelpSection(portal):
    # create and populate the 'plone_help' folder in the root of the plone
    # the contents are STX files in CMFPlone/docs
    if 'plone_help' not in portal.objectIds():
        portal.invokeFactory(type_name='Folder', id='plone_help')
        plone_help=portal.plone_help
        docs_path=os.path.join(package_home(cmfplone_globals), 'help')
        for filename in os.listdir(docs_path):
            _path=os.path.join(docs_path, filename)
            if not os.path.isdir(_path):
                doc=open(_path, 'r')
                addDocument(plone_help, filename, filename, '',
                            'structured-text', doc.read())
                getattr(plone_help,filename)._setPortalTypeName('Document')

def setupCalendar(portal):
    """ Copied directly from CMFCalendar/Extensions/Install.py """
    self=portal
    from Products.CMFCalendar import Event
    from Products.CMFCore.TypesTool import ContentFactoryMetadata

    out = StringIO()
    typestool = getToolByName(self, 'portal_types')
    skinstool = getToolByName(self, 'portal_skins')
    metadatatool = getToolByName(self, 'portal_metadata')
    catalog = getToolByName(self, 'portal_catalog')
    portal_url = getToolByName(self, 'portal_url')

    # Due to differences in the API's for adding indexes between
    # Zope 2.3 and 2.4, we have to catch them here before we can add
    # our new ones.
    base = aq_base(catalog)
    if hasattr(base, 'addIndex'):
        # Zope 2.4
        addIndex = catalog.addIndex
    else:
        # Zope 2.3 and below
        addIndex = catalog._catalog.addIndex
    if hasattr(base, 'addColumn'):
        # Zope 2.4
        addColumn = catalog.addColumn
    else:
        # Zope 2.3 and below
        addColumn = catalog._catalog.addColumn
    try:
        addIndex('start', 'FieldIndex')
    except ConflictError: raise
    except: pass
    try:
        addIndex('end', 'FieldIndex')
    except ConflictError: raise
    except: pass
    try:
        addColumn('start')
    except ConflictError: raise
    except: pass
    try:
        addColumn('end')
    except ConflictError: raise
    except: pass
    out.write('Added "start" and "end" field indexes and columns to '\
              'the portal_catalog\n')

    # Borrowed from CMFDefault.Portal.PortalGenerator.setupTypes()
    # We loop through anything defined in the factory type information
    # and configure it in the types tool if it doesn't already exist
    for t in Event.factory_type_information:
        if t['id'] not in typestool.objectIds():
            cfm = apply(ContentFactoryMetadata, (), t)
            typestool._setObject(t['id'], cfm)
            out.write('Registered with the types tool\n')
        else:
            out.write('Object "%s" already existed in the types tool\n' % (
                t['id']))

    # Setup a MetadataTool Element Policy for Events
    try:
        metadatatool.addElementPolicy(
            element='Subject',
            content_type='Event',
            is_required=0,
            supply_default=0,
            default_value='',
            enforce_vocabulary=0,
            allowed_vocabulary=('Appointment', 'Convention', 'Meeting',
                                'Social Event', 'Work'),
            REQUEST=None,
            )
    except ConflictError: 
        raise
    except:
        pass
    qi = getToolByName(portal, 'portal_quickinstaller')
    qi.notifyInstalled('CMFCalendar', locked=1)
    out.write('Event added to Metadata element Policies\n')
    return out.getvalue()


def addActionIcons(portal):
    """ After installing QuickInstaller.  We must commit(1) a subtrnx
        so that we will be able to addActionIcons() to the tool
    """

    ai=getToolByName(portal, 'portal_actionicons')
    ai.addActionIcon('plone', 'sendto', 'mail_icon.gif', 'Send-to')
    ai.addActionIcon('plone', 'print', 'print_icon.gif', 'Print')
    ai.addActionIcon('plone', 'rss', 'rss.gif', 'Syndication')
    ai.addActionIcon('plone', 'extedit', 'extedit_icon.gif', 'ExternalEdit')
    ai.addActionIcon('plone', 'addtofavorites', 'site_icon.gif', 'AddToFavorites')
    qi=getToolByName(portal, 'portal_quickinstaller')
    qi.notifyInstalled('CMFActionIcons')

def makePortalRootPortalType(portal):
    """ The root portal object needs to have its own portal_type.
        By default in CMF the root is of 'Folder' type which can
        cause problems when you need finer grain workflow settings
        and update your workflow settings it will change the
        portal root (since its a folder).
    """
    #make Portal portal_type
    portal.portal_types.manage_addTypeInformation(FactoryTypeInformation.meta_type,
                                                  id='Plone Site',
                                                  typeinfo_name='CMFPlone: Plone Site')

    portal._setPortalTypeName('Plone Site')
    #remove all workflow settings from the Portal type
    portal.portal_workflow._chains_by_type['Plone Site']=()
    sprops=portal.portal_properties.site_properties
    use_folder_tabs=sprops.getProperty('use_folder_tabs')
    sprops._updateProperty('use_folder_tabs', tuple(use_folder_tabs)+('Plone Site',))

    #By default Members do not have List folder contents to the root.  I believe this
    # happenes because it starts out with a Folder's workflow.  We could fix this.
    # But I think we can change permission for now and then redo the portal cosntruction.
    portal.manage_permission(ListFolderContents, ('Manager', 'Owner'), acquire=1)
    portal.manage_permission(SetOwnProperties,('Manager','Authenticated'))
    portal.manage_permission(SetOwnPassword,('Manager','Authenticated'))

def addActionsToPortalTypes(portal):
    """ Deprecated.  We are now using a drop-down box on the contentBar """
    typesTool=portal.portal_types
    for ptype in typesTool.objectValues():
        ptype.addAction('content_status_history',
                 name='State',
                 action='string:$object_url/content_status_history',
                 condition='python:object and portal.portal_workflow.getTransitionsFor(object, object.getParentNode())',
                 permission='View',
                 category='object_tabs' )
        if ptype.getId() not in ('Folder', 'Plone Site'):
            ptype.addAction('local_roles',
                     name='Sharing',
                     action="string:${object_url}/folder_localrole_form",
                     condition='',
                     permission='Manage properties',
                     category='object')

def setupExtEditor(portal):
    """ sets the ext_editor property in site properties if the ext editor is available"""
    site_props = portal.portal_properties.site_properties
    # try to import the external editor class
    try:
        from Products.ExternalEditor.ExternalEditor import ExternalEditor
    except ImportError:
        # not available
        safeEditProperty(site_props, 'ext_editor', 0, 'boolean')
    else:
        safeEditProperty(site_props, 'ext_editor', 1, 'boolean')
