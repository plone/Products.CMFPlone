from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.TypesTool import FactoryTypeInformation as fti_klass

def twoBeta2_twoBeta3(portal):
    """ Migrations from to 2.0 beta 2 to 2.0 beta 3 """
    out = []

    # as per bug #1600
    out.append("Altering my preferences to point at the member preferences panel, bug #1600")
    pm = portal.portal_membership
    actions = pm._cloneActions()
    for action in actions:
        if action.id=='preferences':
            txt = action.action.text.replace('personalize_form', 'plone_memberprefs_panel')
            action.action = Expression(txt)
    pm._actions = tuple(actions)

    # ensure that Plone Site is in portal_types
    pt = getToolByName(portal, "portal_types")
    if "Plone Site" not in pt.objectIds():
        pt.manage_addTypeInformation(
            fti_klass.meta_type,
            id = "Plone Site",
            typeinfo_name = "CMFPlone: Plone Site"
        )
        out.append("Adding in Plone Site type")

    # and then in workflow remove any workflow from it
    wt = getToolByName(portal, "portal_workflow")
    wt.setChainForPortalTypes(("Plone Site",), "")
    out.append("Setting up Plone Site workflow")

    # sometimes it seems the migration nukes the
    # default skin, causing a browserDefault error
    ps = getToolByName(portal, "portal_skins")
    if not ps.default_skin:
        out.append("Setting default skin to be Plone Default")
        ps.default_skin = "Plone Default"

    # add in plone_setup to portal_membershipr
    mt=getToolByName(portal, 'portal_membership')
    mt.addAction('plone_setup',
                'Plone Setup',
                'string:${portal_url}/plone_control_panel',
                '', # condition
                ManagePortal,
                'user',
                1),
    out.append("Adding a link for plone setup to the users prefs")

    return out

if __name__=='__main__':
    registerMigrations()
