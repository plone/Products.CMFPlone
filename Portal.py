from Products.CMFPlone import cmfplone_globals
from Products.CMFPlone import custom_policies
from Products.CMFPlone import PloneFolder
from Products.CMFDefault.Portal import CMFSite
from Products.CMFDefault import Document
def listPolicies(): return custom_policies.keys()
def addPolicy(label, klass): custom_policies[label]=klass

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.TypesTool import ContentFactoryMetadata, FactoryTypeInformation
from Products.CMFCore.DirectoryView import addDirectoryViews, registerDirectory
from Products.CMFCore.utils import getToolByName, registerIcon
from Products.CMFDefault import Portal
from Products.CMFCalendar.Extensions import Install as CalendarInstall
from Products.ExternalMethod import ExternalMethod
import Globals
import string
import os, sys, re

__version__='1.0'

default_frontpage=r"""
You can customize this frontpage by clicking the edit tab on this document.
In fact this is how you use your new system. Create folders and put content in those folders.
It's a very simple and powerful system.  

For more information:

- "Plone website":http://www.plone.org

- "Zope community":http://www.zope.org

- "CMF website":http://cmf.zope.org

There are "mailing lists":http://www.zope.org/Resources/MailingLists and 
"recipe websites":http://www.zopelabs.com  
available to provide assistance to you and your new-found Content Management System.
"Online chat":http://www.zope.org/Documentation/Chats is also a nice way
of getting advice and help. 

Please contribute your experiences at the "Plone website":http://www.plone.org

Thanks for using our product.

**The Plone Team**.
"""
class PloneSite(CMFSite):
    """
    Make PloneSite subclass CMFSite and add some methods.
    This will be useful for adding more things later on.
    """
    manage_addPloneFolder = PloneFolder.addPloneFolder

class PloneGenerator(Portal.PortalGenerator):

    klass = PloneSite

    def customizePortalTypes(self, p):
        typesTool=getToolByName(p, 'portal_types')

        typesToSkip=['Folder', 'Discussion Item', 'Topic']
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
        p.manage_delObjects( 'portal_properties' )
        addPloneTool=p.manage_addProduct['CMFPlone'].manage_addTool
        addPloneTool('Plone Membership Tool', None)
        addPloneTool('CMF Workflow Tool', None) 
        addPloneTool('CMF Formulator Tool', None)
        addPloneTool('Plone Utility Tool', None)
        addPloneTool('CMF Navigation Tool', None)
        addPloneTool('Plone Factory Tool', None)
        addPloneTool('Plone Form Tool', None)
        addPloneTool('Plone Properties Tool', None)

        p.manage_permission( CMFCorePermissions.ListFolderContents, ('Manager', 'Member', 'Owner',), acquire=1 )
        p.portal_skins.default_skin='Plone Default'
        p.portal_skins.allow_any=1
        p._setProperty('allowAnonymousViewAbout', 0, 'boolean')
        p._setProperty('localTimeFormat', '%Y-%m-%d', 'string')
        p._setProperty('localLongTimeFormat', '%Y-%m-%d %I:%M %p', 'string')
        p._setProperty('default_language', 'en', 'string')
        p._setProperty('default_charset', 'iso-8859-1', 'string')
        p._setProperty('use_folder_tabs',('Folder',), 'lines')
        p.icon = 'misc_/CMFPlone/plone_icon'
        
        
    def setupPortalContent(self, p):
        p.manage_delObjects('Members')
        PloneFolder.addPloneFolder(p, 'Members')

        p.portal_catalog.unindexObject(p.Members) #unindex Members folder
        p.Members.manage_addProduct['OFSP'].manage_addDTMLMethod('index_html'
                                                                , 'Member list'
                                                                , '<dtml-return roster>')
        p.Members._setPortalTypeName( 'Folder' )                                                                
        Document.addDocument(p, 'index_html')
        o = p.index_html
        o._setPortalTypeName( 'Document' )
        o.setTitle('Welcome to Plone')
        o.setDescription('This welcome page is used to introduce you to the Plone Content Management System.')
        o.edit('structured-text', default_frontpage)
        
        o = p.Members
        o.setTitle('Members')
        o.setDescription("Container for portal members' home directories")
        
        
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
                    , 'plone_3rdParty/XSDHTMLEditor'
                    , 'plone_3rdParty/CMFTopic'
                    , 'plone_3rdParty/CMFCalendar'
                    , 'plone_templates/ui_slots'
                    , 'plone_wysiwyg'
                    , 'plone_ecmascript'
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

    def setupForms(self, p):
        prop_tool = p.portal_properties
        prop_tool.manage_addPropertySheet('navigation_properties', 'Navigation Properties')
        prop_tool.manage_addPropertySheet('form_properties', 'Form Properties')
        
        form_tool = p.portal_form
        form_tool.setValidators('link_edit_form', ['validate_id', 'validate_link_edit'])
        form_tool.setValidators('newsitem_edit_form', ['validate_id', 'validate_newsitem_edit'])
        form_tool.setValidators('document_edit_form', ['validate_id', 'validate_document_edit'])
        form_tool.setValidators('image_edit_form', ['validate_id', 'validate_image_edit'])
        form_tool.setValidators('file_edit_form', ['validate_id', 'validate_file_edit'])
        form_tool.setValidators('folder_edit_form', ['validate_id', 'validate_folder_edit'])
        form_tool.setValidators('event_edit_form', ['validate_id', 'validate_event_edit'])
        form_tool.setValidators('topic_edit_form', ['validate_id', 'validate_topic_edit'])
        form_tool.setValidators('content_status_history', ['validate_content_status_modify'])
        form_tool.setValidators('metadata_edit_form', [])
        form_tool.setValidators('reconfig_form', ['validate_reconfig'])
        form_tool.setValidators('personalize_form', ['validate_personalize'])
        form_tool.setValidators('join_form', ['validate_registration'])
        form_tool.setValidators('metadata_edit_form', ['validate_metadata_edit'])

        # grab the initial portal navigation properties from data/navigation_properties
        nav_tool = p.portal_navigation

        # open and parse the file
        filename='navigation_properties'
        src_file =  open(os.path.join(Globals.package_home(globals()), 'data', filename), 'r')
        src_lines = src_file.readlines()
        src_file.close(); 

        re_comment = re.compile(r"\s*#")
        re_blank = re.compile(r"\s*\n")
        re_transition = re.compile(r"\s*(?P<type>[^\.]*)\.(?P<page>[^\.]*)\.(?P<outcome>[^\s]*)\s*=\s*(?P<action>[^$]*)$")
        for line in src_lines:
            line = line.strip()
            if not re_comment.match(line) and not re_blank.match(line):
                match = re_transition.match(line)
                if match:
                    nav_tool.addTransitionFor(match.group('type'), match.group('page'), match.group('outcome'), match.group('action'))
                else:
                    sys.stderr.write("Unable to parse '%s' in navigation properties file" % (line))

    def setupPlone(self, p): 
        self.customizePortalTypes(p)
        self.customizePortalOptions(p)
        self.setupPloneWorkflow(p)
        self.setupPloneSkins(p)
        self.setupPortalContent(p)
        self.setupForms(p)
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

    p.portal_catalog.refreshCatalog() #after customizations refresh the catalog

    if RESPONSE is not None:
        RESPONSE.redirect(p.absolute_url())
        
def register(context, globals):
    context.registerClass(meta_type='Plone Site',
                          permission='Add CMF Sites',
                          constructors=(manage_addSiteForm,
                                        manage_addSite,) )    
