import zLOG
from Products.CMFCore.Expression import Expression

def twoBeta2_twoBeta3(portal):
    """ Migrations from to 2.0 beta 2 to 2.0 beta 3 """
    out = []

    # as per bug #1600
    out.append("Altering my preferences to point at the member preferences panel")
    pm = portal.portal_membership
    actions = pm._cloneActions()
    for action in actions:
        if action.id=='preferences':
            txt = action.action.text.replace('personalize_form', 'plone_memberprefs_panel')
            action.action = Expression(txt)
    pm._actions = tuple(actions)

    return out
