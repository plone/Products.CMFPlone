"""
Instantiate a CMF Portal with Plone installed and preconfigured in it
"""
from __future__ import nested_scopes

from Products.CMFCore.TypesTool import ContentFactoryMetadata, FactoryTypeInformation
from Products.CMFCore.DirectoryView import addDirectoryViews, registerDirectory
from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod import ExternalMethod

from Globals import package_home
from Acquisition import aq_base
from cStringIO import StringIO
import string

from Acquisition import Implicit
import Persistence
from Extensions.Upgrade import normalize_tabs
cmfplone_globals = {}

import zLOG

def log(message,summary='',severity=0):
	zLOG.LOG('MyDebugLog',severity,summary,message)


# set up stuff, copied from Extensions/Install.py

__version__='0.9'
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

def addSupportOptions(self, outStream):
    """ a little lagniappe """
    skinstool=getToolByName(self, 'portal_skins')
    portal=getToolByName(self, 'portal_url').getPortalObject()
    
    skinstool.default_skin='Plone Default'
    outStream.write( "The Plone skin has now been set as this portals default skin\n" )
    
    MembershipTool=getToolByName(self, 'portal_membership')
    if not MembershipTool.getMemberareaCreationFlag():
        MembershipTool.setMemberareaCreationFlag()
        outStream.write( "Memberarea Creation turned on - existing logins will have folders created upon login.\n" )
    skinstool.allow_any=1 #allow people to arbitrarily select skins
    
    portal._setProperty('allowAnonymousViewAbout', 0, 'boolean')
    outStream.write( "By default anonymous is not allowed to see the About box \n" )

def loadEmergingExample(self, outStream):
    """ 
    installs a sample Website Content and supporting skin 

    PLEASE REMOVE ME.  I DO NOT BELONG HERE.
    """
    return

    import os
    root=getToolByName(self, 'portal_url').getPortalObject()
    
    filename='emerging.zexp'
    src_file =  open(os.path.join(package_home(globals()), 'www', 'examples', filename), 'rb')   
    dest_file = open(os.path.join(INSTANCE_HOME, 'import', filename), 'wb')
    dest_file.write(src_file.read())
    src_file.close(); dest_file.close()

    root.manage_importObject(filename)

    #add skin
    skinstool=getToolByName(self, 'portal_skins')
    try:
        registerDirectory(os.path.join('www'), globals())
        addDirectoryViews( skinstool, os.path.join('www'),  cmfplone_globals ) 
    except Exception, e:
        log('failed to add emerging content FS Directory View' + str(e))
    install_SubSkin(self, outStream, 'Emerging Website', 'examples/emerging')

    #customizations
    website=getattr(root, 'emerging')
    em = ExternalMethod.ExternalMethod(id='bind_emerging_website',
                                       title='',
                                       module='CMFPlone.emerging_utils',
                                       function='bindSkin')
    website._setObject('bind_emerging_website', em)

    try:
        website.manage_addProduct['SiteAccess'].manage_addAccessRule('bind_emerging_website')
    except Exception, e:
	log('error when trying to set AccessRule\n' + str(e))

def populatePortalWithContent(self, outStream):
    """ eventually this will need to be moved out into a seperate module """
    #loadEmergingExample(self, outStream)

    id = 'index_html'
    root = getToolByName(self, 'portal_url').getPortalObject()
    root.invokeFactory('Document', id)
    o = getattr(root, 'index_html')
    o.edit('structured-text', default_frontpage)
    o.setTitle('Welcome to Plone')
    normalize_tabs(self) 
    outStream.write('new frontpage, index_html was created in root of Portal\n')

def changeImmediateViews(self, outStream):
    """ the editing process of CMF is akward, it expects you to fill in metadata before you fill in
        content information.  according to The Plone Way(tm) we create object, edit the object, set
        Properties.  
    """
    typesToSkip=['Folder', 'Discussion Item', 'Topic']
    typesTool=getToolByName(self, 'portal_types')
    outStream.write('Plone is now setting the immediate_view to the object\'s edit view\n')
    for contentType in typesTool.listContentTypes():        
        try:
            typeInfo=typesTool.getTypeInfo(contentType)
            if typeInfo.Type() not in typesToSkip:
                typeObj=getattr(typesTool, typeInfo.getId())
                view=typeInfo.getActionById('edit')
                typeObj._setPropValue('immediate_view', view)
                outStream.write(typeInfo.Type() + " has had its immediate view changed to " + view + '\n')
            
            if typeInfo.Type()=='Folder':
                typeObj=getattr(typesTool, typeInfo.getId())
                view='folder_contents'
                typeObj._setPropValue('immediate_view', view)
                outStream.write(typeInfo.Type() + " has had its immediate view changed to " + view + '\n')
        
        except: 
            pass #gulp!

def checkDependencies(self, outStream):
    """ attempt to report back any dependencies"""

    rootObj=self.aq_parent.restrictedTraverse( ('',) )
    control_panel = getattr(rootObj, 'Control_Panel', None)
    cmfSite=getToolByName(self, 'portal_url').getPortalObject()

    if control_panel:
        products=control_panel.Products
        if not hasattr(products, 'DCWorkflow'):
            outStream.write('You do not have DCWorkflow installed.  it is *highly* recommended you install it.\n')
        else:
            wf_tool=getToolByName(self, 'portal_workflow')
            if 'plone_workflow' not in wf_tool.objectIds():
                wf_tool.manage_addWorkflow(id='plone_workflow', workflow_type='default_workflow (Web-configurable workflow [Revision 2])')            
                wf_tool.setDefaultChain('plone_workflow')            
                wf_tool.updateRoleMappings()
                outStream.write('Created plone_workflow in portal_workflow tool and set it to default.\n')        
    else:
        outStream.write('could not access Root object.\n')

    #in default membership_tool homepages dont participate in workflow
    try:
        if hasattr(cmfSite, 'portal_membership'): 
            cmfSite.manage_delObjects('portal_membership') 
        cmfSite.manage_addProduct['CMFPlone'].manage_addTool(type='Default Membership Tool')
        outStream.write('portal_membership replaced, so homepage creation participates in workflow\n')
    except:
        outStream.write('unable to replace portal_membership\n')
        
    #encapsulates Formulator into a tool, thanks SteveA!
    try:
        if hasattr(cmfSite, 'portal_forms'):
            #cmfSite.manage_delObjects('portal_forms') 
            outStream.write( """ UPGRADE WARNING! portal_forms was not deleted, in case it was apart of the CMFFormsTool\n
                                 if you did not install CMFFormsTool, you may manually delete portal_forms\n\n """ )
        cmfSite.manage_addProduct['CMFPlone'].manage_addTool(type='CMF Formulator Tool')
        outStream.write('portal_form_validation, CMF Form Validation Mechanism added.\n')
    except:
        outStream.write('unable to add portal_forms, the CMF Form Validation Tool\n')
    
    #encapsulates Calendaring functionality into a tool, thanks AndyD!
    try:
        cmfSite.manage_addProduct['CMFPlone'].manage_addTool(type='CMF Calendar Tool')            
        outStream.write('portal_calendar, CMF Calendaring Mechanism added.\n')
    except:
        outStream.write('unable to add portal_calendar, the CMF Calendaring Tool\n')

    #try:
    typesTool = getToolByName(self, 'portal_types')
    typesTool._delObject( 'Folder' )
    try:
        typesTool.manage_addTypeInformation(id='Folder', typeinfo_name='CMFPlone: Plone Folder')
    except:
        # CMF1.3
        typesTool.manage_addTypeInformation(FactoryTypeInformation.meta_type, id='Folder', typeinfo_name='CMFPlone: Plone Folder') 
    outStream.write('Plone folder substituted for default Folder\n')
    #except:
    #    outStream.write('could not substitute Plone folder for default Folder impl\n')
    
def install_SubSkin(self, outStream, skinName, skinFolder):
    """ Installs a subskin, should be just 1 folder that overrides the needed plone /img and stylesheet
        i.e. skinName=Plone XP, skinFolder=plone_xp
    """
    skinstool=getToolByName(self, 'portal_skins')
    path = skinstool.getSkinPath('Plone Default') #default
    if not path:
        outStream.write('Plone skin not found, aborting\n')
        return
    path = map( string.strip, string.split( path,',' ) )
    try:
        path.insert( path.index( 'custom')+1, skinFolder )
    except ValueError:
        path.append(skinFolder)
    path = string.join( path, ', ' )
    skinstool.addSkinSelection( skinName, path )

def install_PloneSkins(self, out):
    """
        Add a new skin, 'Plone', copying 'ZPT', if it exists, and then
        add our directories only to it.
    """

    skinstool = getToolByName(self, 'portal_skins')
    path = skinstool.getSkinPath( skinstool.getDefaultSkin() )

    if not path:
        try:  
            path = skinstool.getSkinPath( 'ZPT' )
        except:  
            path = skinstool.getSkinPath( 'Basic' )

    path = map( string.strip, string.split( path, ',' ) )
    for plonedir in ( 'plone_content'
                    , 'plone_images'
                    , 'plone_forms'
                    , 'plone_scripts'
		    , 'plone_scripts/form_scripts'
                    , 'plone_styles'
                    , 'plone_templates'
                    , 'plone_3rdParty'
                    , 'plone_calendar'
		    , 'plone_templates/ui_slots'
                    ):
        try:
            path.insert( path.index( 'custom')+1, plonedir )
        except ValueError:
            path.append( plonedir )
    path = string.join( path, ', ' )
    try:
        skinstool.addSkinSelection( 'Plone Default', path )
        out.write( "Added Plone Default skin\n" )
    except:
        out.write( "Plone Default skin unable to install\n" )
    
    try:
        install_SubSkin(self, out, 'Plone Mozilla', 'plone_styles/mozilla')
        out.write('Mozilla subskin successfully installed\n')
    except:
        out.write('Mozilla subskin unable to successfully install\n')

    try:
        install_SubSkin(self, out, 'Plone XP', 'plone_styles/winxp')
        out.write('XP subskin successfully installed\n')
    except:
        out.write('Plone XP subskin unable to install\n')

    try:  
        addDirectoryViews( skinstool, 'skins', cmfplone_globals )
        out.write( "Added CMFPlone directory views to portal_skins\n" )
    except:
        out.write( 'Unable to add CMFPlone directory view to portal_skins \n ')

    try:
        changeImmediateViews(self, out)
        out.write( "\n\n\n!!Extra Configuration Done!!\n" )
    except:
        out.write( "\n Extra Configuration unable to Complete\n "  )

    try:
        skinstool.request_varname='plone_skin'
	out.write('\n skin request variable changed to plone_skin\n')
    except:
        out.write(' request varaiable could not be changed \n')

    try:
        populatePortalWithContent(self, out)
    except:
        out.write( 'could not populate plone root with default content\n' )

def installExternalMethods(self, outStream):
    """ Installs two external methods so that the plone_calendar will operate correctly.
        I hope to refactor this so that the external methods will disappear.
    """

    if not 'install_events' in self.objectIds():
        em = ExternalMethod.ExternalMethod(id='install_events',
                                           title='',
                                           module='CMFCalendar.Install',
                                           function='install')
        self._setObject('install_events', em)

    outStream.write('Installed calendar external methods.\n')

    if not 'getWorklists' in self.objectIds():
        em = ExternalMethod.ExternalMethod(id='getWorklists',
                                           title='Plone worklists',
                                           module='CMFPlone.PloneWorklists',
                                           function='getWorklists')
        self._setObject('getWorklists', em)

    outStream.write('Installed getWorklists external method.\n')
    if not 'migrateFolders' in self.objectIds():
        em = ExternalMethod.ExternalMethod(id='migrateFolders', 
                                           title='migrate to Plone Folders',
                                           module='CMFPlone.migrateFolders',
                                           function='migrateFolders')
        self._setObject('migrateFolders', em)
    outStream.write('Installed migrateFolders external method.\n')

def install(self):
    """ Register the Plone Skins with portal_skins and friends """
    skinstool = getToolByName(self, 'portal_skins')

    out = StringIO()
    out.write( 'Plone installation tool v' + str(__version__) + '\n')

    checkDependencies( self, out)
    if skinstool.getSkinPath( 'Plone' ) is not None:
        out.write( 'Plone skin exists ! \n' )

    if skinstool.getSkinPath( 'Plone' ) is None:
        install_PloneSkins(self, out)
    else:
        out.write( "Plone skin already exists. Remove before installing again.\n" )

    try:
        addSupportOptions(self, out)
        out.write('added membership options such as default skin to Plone and allow people to pick skins\n')
    except:
        out.write('unable to modify membership options for members\n')

    installExternalMethods(self, out)
    
    # this runs the newly created 'install_events' script
    self.install_events()

    return out.getvalue()


# the real Factory stuff

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

manage_addSiteForm = PageTemplateFile('www/addSite', globals())
manage_addSiteForm.__name__ = 'addSite'
from Products.CMFDefault.Portal import manage_addCMFSite
def manage_addSite(self, id, title='Portal', description='',
                         create_userfolder=1,
                         email_from_address='postmaster@localhost',
                         email_from_name='Portal Administrator',
                         validate_email=0, RESPONSE=None):
    '''
    Adds a Plone portal instance.
    '''
    manage_addCMFSite(self, id, title, description, create_userfolder,
                         email_from_address, email_from_name,
                         validate_email, RESPONSE)
    install(getattr(self, id))

# register with Product Context

def register(context, globals):
    context.registerClass(meta_type='Plone Site',
                          permission='Add CMF Sites',
                          constructors=(manage_addSiteForm,
                                        manage_addSite,
                                        ))
    global cmfplone_globals
    cmfplone_globals = globals
