"""
Instantiate a CMF Portal with Plone installed and preconfigured in it
"""
from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod import ExternalMethod

from Acquisition import aq_base
from cStringIO import StringIO
import string
import string 

from Acquisition import Implicit
import Persistence

cmfplone_globals = {}


# set up stuff, copied from Extensions/Install.py

__version__='0.9'
default_frontpage=r"""
<p> You can customize the frontpage by editing the index_html Document that is in your root folder.
In fact this is how you use your new system.  Create folders and put content in those folders. ;)
Its a very simple and powerful system.  </p>
<p> For more information: </p>
<ul> 
   <li> Plone website - <a href="http://www.plone.org">plone.org</a> </li>
   <li> ZOPE site - <a href="http://www.zope.org">ZOPE</a> </li>
   <li> CMF website - <a href="http://cmf.zope.org">CMF</a> </li>
</ul>
<p> There is a enormous user community for you to take advantage of. 
There are <a href="http://www.zope.org/Resources/MailingLists">mailing lists</a>, 
<a href="http://www.zopelabs.com/">websites</a>, and 
<a href="http://www.zope.org/Documentation/Chats">online chat</a> mediums available to 
to provide you assistance to your new found Content Management System.</p>
<p> Please contribute your experiences at the <a href="http://www.plone.org">Plone website</a>. <br/><br/>
Thanks,<br/>
The Plone Team.
</p>"""

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

def populatePortalWithContent(self, outStream):
    """ eventually this will need to be moved out into a seperate module """
    id = 'index_html'
    root = getToolByName(self, 'portal_url').getPortalObject()
    root.invokeFactory('Document', id)
    o = getattr(root, 'index_html')
    o.edit('html', default_frontpage)
    o.setTitle('Welcome to Plone')
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
    """ attempt to report back any dependncies"""

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
    typesTool.manage_addTypeInformation(id='Folder', typeinfo_name='CMFPlone: Plone Folder') 
    outStream.write('Plone folder substituted for default Folder\n')
    #except:
    #    outStream.write('could not substitute Plone folder for default Folder impl\n')
    
def install_SubSkin(self, outStream, skinName, skinFolder):
    """ Installs a subskin, should be just 1 folder that overrides the needed plone /img and stylesheet
        i.e. skinName=Plone IE5.5, skinFolder=plone_ie55
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
                    , 'plone_form_scripts'
                    , 'plone_scripts'
                    , 'plone_styles'
                    , 'plone_templates'
                    , 'plone_3rdParty'
                    , 'plone_calendar'
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
        install_SubSkin(self, out, 'Plone DHTML', 'plone_ie55')
        out.write('Plone DHTML subskin successfully installed\n')
    except:
        out.write('Plone DHTML subskin unable to install\n')
    
    try:
        install_SubSkin(self, out, 'Plone Mozilla', 'plone_mozilla')
        out.write('Mozilla subskin successfully installed\n')
    except:
        out.write('Mozilla subskin unable to successfully install\n')

    try:
        install_SubSkin(self, out, 'Plone XP', 'plone_xp')
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
