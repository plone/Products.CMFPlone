from Products.CMFCore.CMFCorePermissions import ModifyPortalContent, View, \
     AccessContentsInformation
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Default import setupDefaultWorkflowRev2

def setupDefaultPloneWorkflow(wf):
    # nothing but a default DCWorkflow Rev 2 worflow
    setupDefaultWorkflowRev2(wf)

def createDefaultPloneWorkflow(id):
    ob=DCWorkflowDefinition(id)
    setupDefaultPloneWorkflow(ob)
    ob.setProperties(title='Default Workflow [Plone]')
    return ob

addWorkflowFactory( createDefaultPloneWorkflow, id='plone_workflow'
                  , title='Default Workflow [Plone]')	   

def setupPrivatePloneWorkflow(wf):
    # default plone workflow plus some modifications
    setupDefaultPloneWorkflow(wf)
    wf.states.setInitialState(id='private')
    wf.states.published.permission_roles[View] = ('Member', \
                                                    'Reviewer', 'Manager')
    wf.states.visible.permission_roles[View] = ('Member', \
                                                  'Reviewer', 'Manager')

    wf.states.addState('public')
    sdef=wf.states.public
    sdef.setProperties( title='Publicly available'
                        , transitions=('published', 'reject', 'retract') )
    sdef.setPermission(View, 1, ('Anonymous', 'Authenticated'))
    sdef.setPermission(AccessContentsInformation, 1, \
                       ('Anonymous', 'Authenticated'))
    sdef.setPermission(ModifyPortalContent, 1, ('Manager', ) )
    wf.transitions.addTransition('publicize')
    tdef = wf.transitions.publicize
    tdef.setProperties( title='Publicize content'
                        , new_state_id='public'
                        , actbox_name='Publicize'
                        , actbox_url='%(content_url)s/content_history_form'
                        , props={'guard_permissions':ModifyPortalContent
                                 ,'guard_roles':'Owner;Manager'} )        
    for sdef in wf.states.objectValues():
        if sdef.id != 'public':
            sdef.setProperties( transitions=tuple(sdef.transitions)+\
                                ('publicize',) )
    
def createPrivatePloneWorkflow(id):
    ob=DCWorkflowDefinition(id)
    setupPrivatePloneWorkflow(ob)
    ob.setProperties(title='Private Workflow [Plone]')
    return ob

addWorkflowFactory( createPrivatePloneWorkflow, id='private_plone_workflow'
                  , title='Private Workflow [Plone]')	   

