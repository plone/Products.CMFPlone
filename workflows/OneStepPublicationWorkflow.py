"""
Simple OneStep Publication Workflow (Default Workflow) for a Plone Site
"""
__version__ = "$Revision: 1.1.1.1 $"[11:-2]

from Products.CMFCore.WorkflowTool import addWorkflowFactory

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

def setupOne_step_publication_workflow(wf):
    "..."
    wf.setProperties(title='One step publication workflow')

    for s in ['published', 'private']:
        wf.states.addState(s)
    for t in ['publish', 'make_private']:
        wf.transitions.addTransition(t)
    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        wf.variables.addVariable(v)
    for l in []:
        wf.worklists.addWorklist(l)
    for p in ('Access contents information', 'Modify portal content', 'View', 'Change portal events', 'List folder contents'):
        wf.addManagedPermission(p)
        

    ## Initial State
    wf.states.setInitialState('private')

    ## States initialization
    sdef = wf.states['published']
    sdef.setProperties(title="""Public""",
                       transitions=('make_private',))
    sdef.setPermission('Access contents information', 1, ['Anonymous', 'Authenticated'])
    sdef.setPermission('Modify portal content', 0, ['Manager', 'Owner'])
    sdef.setPermission('View', 0, ['Anonymous', 'Authenticated'])
    sdef.setPermission('Change portal events', 0, ['Manager', 'Owner'])
    sdef.setPermission('List folder contents', 1, ['Anonymous', 'Authenticated'])

    sdef = wf.states['private']
    sdef.setProperties(title="""Visible and editable only by owner""",
                       transitions=('publish',))
    sdef.setPermission('Access contents information', 1, ['Manager', 'Owner'])
    sdef.setPermission('Modify portal content', 0, ['Manager', 'Owner'])
    sdef.setPermission('View', 0, ['Manager', 'Owner'])
    sdef.setPermission('Change portal events', 0, ['Manager', 'Owner'])
    sdef.setPermission('List folder contents', 1, ['Manager', 'Owner'])


    ## Transitions initialization
    tdef = wf.transitions['publish']
    tdef.setProperties(title="""Reviewer publishes content""",
                       new_state_id="""published""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Publish""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_roles': 'Owner'},
                       )

    tdef = wf.transitions['make_private']
    tdef.setProperties(title="""Member makes content private""",
                       new_state_id="""private""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Make private""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_roles': 'Owner'},
                       )

    ## State Variable
    wf.variables.setStateVar('review_state')

    ## Variables initialization
    vdef = wf.variables['review_history']
    vdef.setProperties(description="""Provides access to workflow history""",
                       default_value="""""",
                       default_expr="""state_change/getHistory""",
                       for_catalog=0,
                       for_status=0,
                       update_always=0,
                       props={'guard_permissions': 'Request review; Review portal content'})

    vdef = wf.variables['comments']
    vdef.setProperties(description="""Comments about the last transition""",
                       default_value="""""",
                       default_expr="""python:state_change.kwargs.get('comment', '')""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['time']
    vdef.setProperties(description="""Time of the last transition""",
                       default_value="""""",
                       default_expr="""state_change/getDateTime""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['actor']
    vdef.setProperties(description="""The ID of the user who performed the last transition""",
                       default_value="""""",
                       default_expr="""user/getUserName""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['action']
    vdef.setProperties(description="""The last transition""",
                       default_value="""""",
                       default_expr="""transition/getId|nothing""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    ## Worklists Initialization

def createOne_step_publication_workflow(id):
    "..."
    ob = DCWorkflowDefinition(id)
    setupOne_step_publication_workflow(ob)
    return ob

addWorkflowFactory(createOne_step_publication_workflow,
                   id='one_step_publication_workflow',
                   title='One step publication workflow')
