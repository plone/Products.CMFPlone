from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.CMFCore import CMFCorePermissions
from Products.DCWorkflow.Default import setupDefaultWorkflowRev2

def setupFolderWorkflow(wf):
	setupDefaultWorkflowRev2(wf)
        #Published folders means that anonymous should be able to 'list the folder contents'
        wf.permissions+=(CMFCorePermissions.ListFolderContents, )
        wf.states.published.permission_roles[CMFCorePermissions.ListFolderContents]=['Anonymous',]
        wf.states.published.permission_roles[CMFCorePermissions.ModifyPortalContent]=('Manager', )
        wf.states.deleteStates( ('pending', ) )
        state_priv=wf.states['private']
        state_priv.transitions = ('publish', 'show') 
        state_pub=wf.states['published']
        state_pub.transitions = ('hide', 'retract') 
        wf.transitions.deleteTransitions( ('submit', 'reject') )
        trans_publish=wf.transitions['publish']
        trans_publish_guard=trans_publish.getGuard()
        trans_publish_guard.permissions=(CMFCorePermissions.ModifyPortalContent, )
        trans_publish_guard.roles=('Owner', 'Manager')
    
def createFolderWorkflow(id):
    ob=DCWorkflowDefinition(id)
    setupFolderWorkflow(ob)
    ob.setProperties(title='Folder Workflow [Plone]')
    return ob

addWorkflowFactory( createFolderWorkflow, id='folder_workflow'
                  , title='Folder Workflow [Plone]')	   


def setupPrivateFolderWorkflow(wf):
	setupFolderWorkflow(wf)
	wf.states.visible.permission_roles['View'] = ('Member', 'Reviewer', 'Manager')
        wf.states.published.permission_roles['List folder contents'] = ('Authenticated', 'Manager')
        wf.states.published.permission_roles['View'] = ('Member', 'Reviewer', 'Manager')
        wf.states.setInitialState(id='private')
        
        wf.states.addState('public')
        sdef=wf.states.public
        sdef.setProperties( title='Publicly available'
                          , transitions=('published', 'reject', 'retract') ) 
        sdef.setPermission( 'View', 1, ('Anonymous', 'Authenticated') )
        sdef.setPermission( 'Access contents information', 1, ('Anonymous', 'Authenticated') )
        sdef.setPermission( 'List folder contents', 1, ('Anonymous', 'Authenticated') )
        sdef.setPermission( 'Modify portal content', 1, ('Mangager', ) )
        wf.transitions.addTransition('publicize')
        tdef=wf.transitions.publicize
        tdef.setProperties( title='Publicize content'
                          , new_state_id='public'
                          , actbox_name='Publicize'
                          , actbox_url='%(content_url)s/content_history_form'
                          , props={'guard_permissions':'Modify portal content'
                                  ,'guard_roles':'Owner;Manager'} )                                  
        for sdef in wf.states.objectValues():
            if sdef.id != 'public':
                sdef.setProperties( transitions=tuple(sdef.transitions)+\
				    ('publicize',) )
                

def createPrivateFolderWorkflow(id):
    ob=DCWorkflowDefinition(id)
    setupPrivateFolderWorkflow(ob)
    ob.setProperties(title='Private Folder Workflow [Plone]')
    return ob

addWorkflowFactory( createPrivateFolderWorkflow, id='private_folder_workflow'
                  , title='Private Folder Workflow [Plone]')	   

