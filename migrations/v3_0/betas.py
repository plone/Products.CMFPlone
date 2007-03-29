from zope.component import queryUtility

from Products.CMFCore.interfaces import IActionsTool
from Products.ResourceRegistries.interfaces import ICSSRegistry
from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.ActionInformation import ActionInformation

def beta1_beta2(portal):
    """ 3.0-beta1 -> 3.0-beta2
    """

    out = []

    migrateHistoryTab(portal, out)
    changeOrderOfActionProviders(portal, out)
    addControlpanelStylesheet(portal, out)

    return out


def addNewBeta2CSSFiles(portal, out):
    # add new css files to the portal_css registries
    cssreg = queryUtility(ICSSRegistry)
    stylesheet_ids = cssreg.getResourceIds()
    if 'controlpanel.css' not in stylesheet_ids:
        cssreg.registerStylesheet('controlpanel.css', media='screen')
        cssreg.moveResourceAfter('controlpanel.css', 'portlets.css')
        out.append("Added controlpanel.css to the registry")

def migrateHistoryTab(portal, out):
    portal_actions = queryUtility(IActionsTool)
    if portal_actions is not None:
        objects = getattr(portal_actions, 'object', None)
        if objects is not None:
            if 'rss' in objects.objectIds():
                objects.manage_renameObjects(['rss'], ['history'])
                out.append('Migrated history action.')

def changeOrderOfActionProviders(portal, out):
    portal_actions = queryUtility(IActionsTool)
    if portal_actions is not None:
        portal_actions.deleteActionProvider('portal_actions')
        portal_actions.addActionProvider('portal_actions')
        out.append('Changed the order of action providers.')
