from __future__ import nested_scopes
    
from Products.CMFPlone import cmfplone_globals
from Products.CMFPlone import custom_policies
from Products.CMFPlone import PloneFolder
from Products.CMFDefault.Portal import CMFSite
from Products.CMFDefault import Document
def listPolicies(): return custom_policies.keys()
def addPolicy(label, klass): custom_policies[label]=klass

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.TypesTool import FactoryTypeInformation

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
You can customize this frontpage by clicking the edit tab on this document if you
have the correct permissions. Create folders and put content in those folders.
Folders will show up in the navigation box if they are published. It's a very 
simple and powerful system.  

For more information:

- "Plone website":http://www.plone.org

- "Zope community":http://www.zope.org

- "CMF website":http://cmf.zope.org

There are "mailing lists":http://plone.org/development/lists and 
"recipe websites":http://www.zopelabs.com  
available to provide assistance to you and your new-found Content Management System.
"Online chat":http://plone.org/development/chat is also a nice way
of getting advice and help. 

Please contribute your experiences at the "Plone website":http://www.plone.org

Thanks for using our product.

"Plone":img:logoIcon.gif  "The Plone Team":http://plone.org/about/team
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
        def exists(id):
            return id in p.objectIds()
        if exists('portal_membership'):
            p.manage_delObjects( 'portal_membership' )
        if exists('portal_workflow'):
            p.manage_delObjects( 'portal_workflow' )
        if exists('portal_properties'):
            p.manage_delObjects( 'portal_properties' )

        addPloneTool=p.manage_addProduct['CMFPlone'].manage_addTool

        addPloneTool('Plone Membership Tool', None)
        addPloneTool('CMF Workflow Tool', None) 
        if not exists('portal_form_validation'):
            addPloneTool('CMF Formulator Tool', None)
        if not exists('plone_utils'):
            addPloneTool('Plone Utility Tool', None)
        if not exists('portal_navigation'):
            addPloneTool('CMF Navigation Tool', None)
        if not exists('portal_factory'):
            addPloneTool('Plone Factory Tool', None)
        if not exists('portal_form'):
            addPloneTool('Plone Form Tool', None)
        if not exists('portal_properties'):
            addPloneTool('Plone Properties Tool', None)
        if not exists('portal_migration'):
            addPloneTool('Plone Migration Tool', None)

        p.manage_permission( CMFCorePermissions.ListFolderContents, \
                             ('Manager', 'Member', 'Owner',), acquire=1 )
        p.portal_skins.default_skin='Plone Default'
        p.portal_skins.allow_any=1

        p.icon = 'misc_/CMFPlone/plone_icon'
        
        
    def setupPortalContent(self, p):
        p.manage_delObjects('Members')
        PloneFolder.addPloneFolder(p, 'Members')

        p.portal_catalog.unindexObject(p.Members) #unindex Members folder
        p.Members.manage_addProduct['OFSP'].manage_addDTMLMethod('index_html'
                                                                , 'Member list'
                                                                , '<dtml-return member_search_form>')
        p.Members._setPortalTypeName( 'Folder' )                                                               
        Document.addDocument(p, 'index_html')
        o = p.index_html
        o._setPortalTypeName( 'Document' )
        o.setTitle('Welcome to Plone')
        o.setDescription('This welcome page is used to introduce you'+\
                         ' to the Plone Content Management System.')
        o.edit('structured-text', default_frontpage)
        
        o = p.Members
        o.setTitle('Members')
        o.setDescription("Container for portal members' home directories")
        
        
    def setupPloneWorkflow(self, p):      
        wf_tool=p.portal_workflow
        wf_tool.manage_addWorkflow( id='plone_workflow'
                                  , workflow_type='plone_workflow '+\
                                    '(Default Workflow [Plone])')
        wf_tool.setDefaultChain('plone_workflow')

        wf_tool.manage_addWorkflow( id='folder_workflow'
                                , workflow_type='folder_workflow '+\
                                  '(Folder Workflow [Plone])')
        wf_tool.setChainForPortalTypes( ('Folder','Topic'), 'folder_workflow')

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

        self.setupSecondarySkin(sk_tool, 'Plone Autumn',        'plone_styles/autumn')
        self.setupSecondarySkin(sk_tool, 'Plone Core',          'plone_styles/core')
        self.setupSecondarySkin(sk_tool, 'Plone Core Inverted', 'plone_styles/core_inverted')
        self.setupSecondarySkin(sk_tool, 'Plone Corporate',     'plone_styles/corporate')
        self.setupSecondarySkin(sk_tool, 'Plone Greensleeves',  'plone_styles/greensleeves')
        self.setupSecondarySkin(sk_tool, 'Plone Kitty',         'plone_styles/kitty')
        self.setupSecondarySkin(sk_tool, 'Plone Mozilla',       'plone_styles/mozilla')
        self.setupSecondarySkin(sk_tool, 'Plone Mozilla New',   'plone_styles/mozilla_new')
        self.setupSecondarySkin(sk_tool, 'Plone Prime',         'plone_styles/prime')
        self.setupSecondarySkin(sk_tool, 'Plone Zed',           'plone_styles/zed')

        addDirectoryViews( sk_tool, 'skins', cmfplone_globals )
        
        sk_tool.request_varname='plone_skin'

    def setupForms(self, p):
        prop_tool = p.portal_properties
        prop_tool.manage_addPropertySheet('navigation_properties', \
                                          'Navigation Properties')
        prop_tool.manage_addPropertySheet('form_properties', 'Form Properties')

        form_tool = p.portal_form
        form_tool.setValidators('link_edit_form', \
                                ['validate_id', 'validate_link_edit'])
        form_tool.setValidators('newsitem_edit_form', \
                                ['validate_id', 'validate_newsitem_edit'])
        form_tool.setValidators('document_edit_form', \
                                ['validate_id', 'validate_document_edit'])
        form_tool.setValidators('image_edit_form', \
                                ['validate_id', 'validate_image_edit'])
        form_tool.setValidators('file_edit_form', \
                                ['validate_id', 'validate_file_edit'])
        form_tool.setValidators('folder_edit_form', \
                                ['validate_id', 'validate_folder_edit'])
        form_tool.setValidators('event_edit_form', \
                                ['validate_id', 'validate_event_edit'])
        form_tool.setValidators('topic_edit_form', \
                                ['validate_id', 'validate_topic_edit'])
        form_tool.setValidators('content_status_history', \
                                ['validate_content_status_modify'])
        form_tool.setValidators('metadata_edit_form', [])
        form_tool.setValidators('reconfig_form', \
                                ['validate_reconfig'])
        form_tool.setValidators('personalize_form', \
                                ['validate_personalize'])
        form_tool.setValidators('join_form', \
                                ['validate_registration'])
        form_tool.setValidators('metadata_edit_form', \
                                ['validate_metadata_edit'])
        
        #set up properties for StatelessTreeNav
        from Products.CMFPlone.StatelessTreeNav \
             import setupNavTreePropertySheet
        setupNavTreePropertySheet(prop_tool)

        # grab the initial portal navigation properties
        # from data/navigation_properties
        nav_tool = getToolByName(p, 'portal_navigation')

        # open and parse the file
        filename='navigation_properties'
        src_file = open(os.path.join(Globals.package_home(globals()), 'data', filename), 'r')
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

        m = p.portal_migration
        m.setInstanceVersion('1.0beta2')
        m.upgrade()
        
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
    customization_policy=None
    if listPolicies() and custom_policy:
        customization_policy=custom_policies[custom_policy]
        # Save customization policy results on a object
        result = customization_policy.customize(p)
        if result:
            p.invokeFactory(type_name='Document', id='CustomizationLog')
            p.CustomizationLog.edit(text_format='plain', text=result)

    # reindex catalog and workflow settings
    p.portal_catalog.refreshCatalog()     
    p.portal_workflow.updateRoleMappings() 

    if RESPONSE is not None:
        RESPONSE.redirect(p.absolute_url())
        
def register(context, globals):
    context.registerClass(meta_type='Plone Site',
                          permission='Add CMF Sites',
                          constructors=(manage_addSiteForm,
                                        manage_addSite,) )    
