from Products.CMFPlone import cmfplone_globals
from Products.CMFPlone import custom_policies
def listPolicies(): return custom_policies.keys()
def addPolicy(label, klass): custom_policies[label]=klass

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.TypesTool import ContentFactoryMetadata, FactoryTypeInformation
from Products.CMFCore.DirectoryView import addDirectoryViews, registerDirectory
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault import Portal
from Products.CMFCalendar.Extensions import Install as CalendarInstall
from Products.ExternalMethod import ExternalMethod
import Globals
import string

__version__='1.0'

default_frontpage=r"""
You can customize this frontpage by clicking the edit tab on this document.
In fact this is how you use your new system. Create folders and put content in those folders.
It's a very simple and powerful system.  

For more information:

- "Plone website":http://www.plone.org

- "Zope community":http://www.zope.org

- "CMF website":http://cmf.zope.org

There is an enormous user community for you to take advantage of. 
There are "mailing lists":http://www.zope.org/Resources/MailingLists and 
"recipe websites":http://www.zopelabs.com  
available to provide assistance to you and your new-found Content Management System.
"Online chat":http://www.zope.org/Documentation/Chats is also a nice way
of getting advice and help. 

Please contribute your experiences at the "Plone website":http://www.plone.org

Thanks for using our product.

**The Plone Team**.
"""

class PloneGenerator(Portal.PortalGenerator):

    def customizePortalTypes(self, p):
        typesToSkip=['Folder', 'Discussion Item', 'Topic']
        typesTool=getToolByName(p, 'portal_types')
        typesTool._delObject('Folder')
        typesTool.manage_addTypeInformation(FactoryTypeInformation.meta_type
                                           , id='Folder'
                                           , typeinfo_name='CMFPlone: Plone Folder')
        for contentType in typesTool.listContentTypes():        
            typeInfo=typesTool.getTypeInfo(contentType)
            if typeInfo.getId() not in typesToSkip:
                typeObj=getattr(typesTool, typeInfo.getId())
                view=typeInfo.getActionById('edit')
                typeObj._setPropValue('immediate_view', view)       
            if typeInfo.getId()=='Folder':
                typeObj=getattr(typesTool, typeInfo.getId())
                view='folder_contents'
                typeObj._setPropValue('immediate_view', view)

    def customizePortalOptions(self, p):
        p.manage_delObjects( 'portal_membership' )
        p.manage_delObjects( 'portal_workflow' )
        addPloneTool=p.manage_addProduct['CMFPlone'].manage_addTool
        addPloneTool('Plone Membership Tool', None)
        addPloneTool('CMF Workflow Tool', None) 
        addPloneTool('CMF Formulator Tool', None)
        addPloneTool('Plone Utility Tool', None)

        p.manage_permission( CMFCorePermissions.ListFolderContents, ('Manager', 'Member', 'Owner',), acquire=1 )
        p.portal_skins.default_skin='Plone Default'
        p.portal_skins.allow_any=1
        p._setProperty('allowAnonymousViewAbout', 0, 'boolean')
        p._setProperty('localTimeFormat', '%Y-%m-%d', 'string')
        p._setProperty('localLongTimeFormat', '%Y-%m-%d %I:%M %p', 'string')
        
    def setupPortalContent(self, p):
        p.manage_delObjects('Members')
        p.invokeFactory('Folder', 'Members')
        p.Members.manage_addProduct['OFSP'].manage_addDTMLMethod('index_html'
                                                                , 'Member list'
                                                                , '<dtml-return roster>')
        p.invokeFactory('Document', 'frontpage')
        o = p.frontpage
        o.setTitle('Welcome to Plone')
        o.setDescription('This welcome page is used to introduce you to the Plone Content Management System.')
        o.edit('structured-text', default_frontpage)
        
        skins=getToolByName(p, 'portal_skins')
        skins.plone_templates.frontpage_template.manage_doCustomize(folder_path='custom')
        p.manage_pasteObjects( skins.custom.manage_cutObjects('frontpage_template') )
        p.manage_renameObjects( ('frontpage_template',), ('index_html',) )

    def setupPloneWorkflow(self, p):      
        wf_tool=p.portal_workflow
        wf_tool.manage_addWorkflow( id='plone_workflow'
                                  , workflow_type='default_workflow (Web-configurable workflow [Revision 2])')
        wf_tool.setDefaultChain('plone_workflow')

        wf_tool.manage_addWorkflow( id='folder_workflow'
                                  , workflow_type='default_workflow (Web-configurable workflow [Revision 2])')
        folder_wf = wf_tool['folder_workflow']
        #Published folders means that anonymous should be able to 'list the folder contents'
        folder_wf.permissions+=(CMFCorePermissions.ListFolderContents, )
        folder_wf.states.published.permission_roles[CMFCorePermissions.ListFolderContents]=['Anonymous',]
        folder_wf.states.deleteStates( ('pending', ) )
        state_priv=folder_wf.states['private']
        state_priv.transitions = ('publish', 'show') 
        state_pub=folder_wf.states['published']
        state_pub.transitions = ('hide', 'retract') 
        folder_wf.transitions.deleteTransitions( ('submit', 'reject') )
        trans_publish=folder_wf.transitions['publish']
        trans_publish_guard=trans_publish.getGuard()
        trans_publish_guard.permissions=(CMFCorePermissions.ModifyPortalContent, )
        trans_publish_guard.roles=('Owner', 'Manager')
        wf_tool.setChainForPortalTypes( ('Folder',), 'folder_workflow')

        wf_tool.updateRoleMappings()

    def setupSecondarySkin(self, skin_tool, skin_title, directory_id):        
        path=[elem.strip() for elem in skin_tool.getSkinPath('Plone Default').split(',')]
        path.insert(path.index('custom')+1, directory_id)
        skin_tool.addSkinSelection(skin_title, ','.join(path))
        
    def setupPloneSkins(self, p):
        sk_tool=p.portal_skins
        path=[elem.strip() for elem in sk_tool.getSkinPath('Basic').split(',')]
        for plonedir in ( 'plone_content'
                    , 'plone_images'
                    , 'plone_forms'
                    , 'plone_scripts'
                    , 'plone_scripts/form_scripts'
                    , 'plone_styles'
                    , 'plone_templates'
                    , 'plone_3rdParty'
                    , 'plone_3rdParty/CMFTopic'
                    , 'plone_calendar'
                    , 'plone_templates/ui_slots'
                    , 'plone_wysiwyg'
                    ):
            try:
                path.insert( path.index( 'custom')+1, plonedir )
            except ValueError:
                path.append( plonedir )
        path=','.join(path)
        sk_tool.addSkinSelection('Plone Default', path)
        self.setupSecondarySkin(sk_tool, 'Plone Mozilla', 'plone_styles/mozilla')
        self.setupSecondarySkin(sk_tool, 'Plone XP', 'plone_styles/winxp')
        addDirectoryViews( sk_tool, 'skins', cmfplone_globals )
        sk_tool.request_varname='plone_skin'
        
    def setupPlone(self, p): 
        self.customizePortalTypes(p)
        self.customizePortalOptions(p)
        self.setupPloneWorkflow(p)
        self.setupPloneSkins(p)
        self.setupPortalContent(p)
        CalendarInstall.install(p)
        
    def create(self, parent, id, create_userfolder):
        id = str(id)
        portal = self.klass(id=id)
        parent._setObject(id, portal)
        p = parent._getOb(id) # Return the fully wrapped object
        self.setup(p, create_userfolder)
        self.setupPlone(p)
        return p
    
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
manage_addSiteForm = PageTemplateFile('www/addSite', globals())
manage_addSiteForm.__name__ = 'addSite'
from Products.CMFDefault.Portal import manage_addCMFSite
def manage_addSite(self, id, title='Portal', description='',
                   create_userfolder=1,
                   email_from_address='postmaster@localhost',
                   email_from_name='Portal Administrator',
                   validate_email=0,
                   custom_policy='',
		   RESPONSE=None):
    """ Plone Site factory """
    gen = PloneGenerator()
    p = gen.create(self, id.strip(), create_userfolder)
    gen.setupDefaultProperties(p, title, description,
                               email_from_address, email_from_name,
                               validate_email)
    if listPolicies() and custom_policy:
        o=custom_policies[custom_policy]
        o.customize(p)
    if RESPONSE is not None:
        RESPONSE.redirect(p.absolute_url())
        
def register(context, globals):
    context.registerClass(meta_type='Plone Site',
                          permission='Add CMF Sites',
                          constructors=(manage_addSiteForm,
                                        manage_addSite,) )    
