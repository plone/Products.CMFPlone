"""
Community Default Workflow for Plone Sites
"""
__version__ = "$Revision: 1.1.1.1 $"[11:-2]

from Products.CMFCore.WorkflowTool import addWorkflowFactory

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

def setupCommunity_workflow(wf):
    "..."
    wf.setProperties(title='Community workflow')

    for s in ['public_draft', 'private', 'published', 'pending_retract', 'pending_publish']:
        wf.states.addState(s)
    for t in ['publish', 'cancel_publish', 'cancel_retract', 'retract', 'submit_retract', 'submit_publish', 'reject_retract', 'reject_publish', 'make_private', 'publish_as_draft']:
        wf.transitions.addTransition(t)
    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        wf.variables.addVariable(v)
    for l in ['reviewer_queue']:
        wf.worklists.addWorklist(l)
    for p in ('Access contents information', 'Modify portal content', 'View', 'Change portal events', 'List folder contents'):
        wf.addManagedPermission(p)
        

    ## Initial State
    wf.states.setInitialState('public_draft')

    ## States initialization
    sdef = wf.states['public_draft']
    sdef.setProperties(title="""PublicDraft""",
                       transitions=('make_private', 'publish', 'submit_publish'))
    sdef.setPermission('Access contents information', 1, ['Anonymous', 'Authenticated'])
    sdef.setPermission('Modify portal content', 0, ['Manager', 'Owner'])
    sdef.setPermission('View', 0, ['Anonymous', 'Authenticated'])
    sdef.setPermission('Change portal events', 0, [])
    sdef.setPermission('List folder contents', 1, ['Anonymous', 'Authenticated'])

    sdef = wf.states['private']
    sdef.setProperties(title="""Private""",
                       transitions=('publish_as_draft',))
    sdef.setPermission('Access contents information', 1, ['Manager', 'Owner'])
    sdef.setPermission('Modify portal content', 0, ['Manager', 'Owner'])
    sdef.setPermission('View', 0, ['Manager', 'Owner'])
    sdef.setPermission('Change portal events', 0, ['Manager', 'Owner'])
    sdef.setPermission('List folder contents', 1, ['Manager', 'Owner'])

    sdef = wf.states['published']
    sdef.setProperties(title="""Public""",
                       transitions=('retract', 'submit_retract'))
    sdef.setPermission('Access contents information', 1, ['Anonymous', 'Authenticated'])
    sdef.setPermission('Modify portal content', 0, ['Manager'])
    sdef.setPermission('View', 0, ['Anonymous', 'Authenticated'])
    sdef.setPermission('Change portal events', 0, ['Manager'])
    sdef.setPermission('List folder contents', 1, ['Anonymous', 'Authenticated'])

    sdef = wf.states['pending_retract']
    sdef.setProperties(title="""PendingRetract""",
                       transitions=('reject_publish', 'reject_retract', 'retract'))
    sdef.setPermission('Access contents information', 1, ['Anonymous', 'Authenticated'])
    sdef.setPermission('Modify portal content', 0, ['Manager'])
    sdef.setPermission('View', 0, ['Anonymous', 'Authenticated'])
    sdef.setPermission('Change portal events', 0, [])
    sdef.setPermission('List folder contents', 1, ['Anonymous', 'Authenticated'])

    sdef = wf.states['pending_publish']
    sdef.setProperties(title="""Pending""",
                       transitions=('cancel_publish', 'publish', 'reject_publish'))
    sdef.setPermission('Access contents information', 1, ['Anonymous', 'Authenticated'])
    sdef.setPermission('Modify portal content', 0, ['Manager', 'Reviewer'])
    sdef.setPermission('View', 0, ['Anonymous', 'Authenticated'])
    sdef.setPermission('Change portal events', 0, [])
    sdef.setPermission('List folder contents', 1, ['Anonymous', 'Authenticated'])


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
                       props={'guard_roles': 'Reviewer'},
                       )

    tdef = wf.transitions['cancel_publish']
    tdef.setProperties(title="""""",
                       new_state_id="""public_draft""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""cancel publish""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_roles': 'Owner'},
                       )

    tdef = wf.transitions['cancel_retract']
    tdef.setProperties(title="""""",
                       new_state_id="""published""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""cancel retract""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_roles': 'Owner'},
                       )

    tdef = wf.transitions['retract']
    tdef.setProperties(title="""Owner retracts content""",
                       new_state_id="""public_draft""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Retract""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_roles': 'Reviewer'},
                       )

    tdef = wf.transitions['submit_retract']
    tdef.setProperties(title="""submit retract""",
                       new_state_id="""pending_retract""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Submit Retract""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_roles': 'Owner'},
                       )

    tdef = wf.transitions['submit_publish']
    tdef.setProperties(title="""submit publish""",
                       new_state_id="""pending_publish""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Submit""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_roles': 'Owner'},
                       )

    tdef = wf.transitions['reject_retract']
    tdef.setProperties(title="""""",
                       new_state_id="""published""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""reject retract""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_roles': 'Reviewer'},
                       )

    tdef = wf.transitions['reject_publish']
    tdef.setProperties(title="""Reviewer rejects content""",
                       new_state_id="""public_draft""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Reject""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_roles': 'Reviewer'},
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

    tdef = wf.transitions['publish_as_draft']
    tdef.setProperties(title="""Owner publishes content as draft""",
                       new_state_id="""public_draft""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""PublishAsDraft""",
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
    ldef = wf.worklists['reviewer_queue']
    ldef.setProperties(description="""Reviewer tasks""",
                       actbox_name="""Pending (%(count)d)""",
                       actbox_url="""%(portal_url)s/search?review_state=pending""",
                       actbox_category="""global""",
                       props={'guard_permissions': 'Review portal content', 'var_match_review_state': 'pending_publish'})


def createCommunity_workflow(id):
    "..."
    ob = DCWorkflowDefinition(id)
    setupCommunity_workflow(ob)
    return ob

addWorkflowFactory(createCommunity_workflow,
                   id='community_workflow',
                   title='Community workflow')
