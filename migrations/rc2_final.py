from Products.CMFPlone import MigrationTool
from Products.CMFCore.Expression import Expression

def rc2Final(portal):
    """ Upgrade from Plone 1.0 RC2 to Final"""

    p = portal.portal_properties.site_properties
    e = getattr(p, 'available_editors', [])

    # if there is the old editor in there,
    # change it to the new one
    if 'XSDHTMLEditor' in e:
        elist = list(e)
        elist.remove('XSDHTMLEditor')
        p._updateProperty('available_editors', elist)

    #update State action in portal_actions so that DTML Documents work.
    #XXX We really need to put the 'State' action on individual portal_type definitions
    #    The reason being is that its really *lazy* and hackish to define it as a global
    #    across all types.  Things like CMFCollector dont work w/ this workflow.
    at = portal.portal_actions
    actions = at._cloneActions()
    for action in actions:
        if action.id=='content_status_history':
            statexpr=Expression('python:object and portal.portal_workflow.getTransitionsFor(object, object.getParentNode())')
            action.title='State'
            action.condition=statexpr
    at._actions = tuple(actions)

    nav_props = portal.portal_properties.navigation_properties
    nav_props._updateProperty('default.content_status_modify.failure', 
        'content_status_history')
