from zope.app.component.interfaces import ISite
from zope.component.globalregistry import base
from zope.component.persistentregistry import PersistentComponents

from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.ActionInformation import ActionCategory
from Products.CMFCore.utils import getToolByName
from Products.Five.component import enableSite
from Products.Five.component.interfaces import IObjectManagerSite

def three0_alpha1(portal):
    """2.5.x -> 3.0-alpha1
    """
    out = []

    # Make the portal a Zope3 site
    enableZope3Site(portal, out)

    # Migrate old ActionInformation to Actions and move them to the actions tool
    migrateOldActions(portal, out)

    # Add new css files to RR
    addNewCSSFiles(portal, out)

    # Actions should gain a i18n_domain now, so their title and description are
    # returned as Messages
    updateActionsI18NDomain(portal, out)

    # Type information should gain a i18n_domain now, so their title and
    # description are returned as Messages
    updateFTII18NDomain(portal, out)

    return out


def enableZope3Site(portal, out):
    if not ISite.providedBy(portal):
        enableSite(portal, iface=IObjectManagerSite)

        components = PersistentComponents()
        components.__bases__ = (base,)
        portal.setSiteManager(components)

        out.append('Made the portal a Zope3 site.')

def migrateOldActions(portal, out):
    new_providers = portal.portal_actions.listActionProviders()
    # We don't need to operate on the providers that are still valid and
    # should ignore the control panel as well
    providers = [obj for obj in portal.objectValues()
                     if hasattr(obj, '_actions') and obj.getId() not in
                     new_providers and obj.getId() != 'portal_controlpanel']
    non_empty_providers = [p for p in providers if len(p._actions) > 0]
    for provider in non_empty_providers:
        for action in provider._actions:
            category = action.category
            # check if the category already exists, otherwise create it
            new_category = getattr(portal.portal_actions, category, None)
            if new_category is None:
                portal.portal_actions[category] = ActionCategory(id=category)
                new_category = portal.portal_actions[category]

            new_action = Action(action.id,
                title=action.title,
                description=action.description,
                url_expr=action.action.text,
                available_expr=action.condition.text,
                permissions=action.permissions,
                visible = action.visible
            )
            # Only add an action if there isn't one with that name already
            if getattr(new_category, action.id, None) is None:
                new_category[action.id] = new_action

        # Remove old actions from migrated providers
        provider._actions = ()

def addNewCSSFiles(portal, out):
    # add new css files to the portal_css registries
    cssreg = getToolByName(portal, 'portal_css', None)
    stylesheet_ids = cssreg.getResourceIds()
    if 'navtree.css' not in stylesheet_ids:
        cssreg.registerStylesheet('navtree.css', media='screen')
        cssreg.moveResourceAfter('navtree.css', 'textLarge.css')
        out.append("Added navtree.css to the registry")
    if 'invisibles.css' not in stylesheet_ids:
        cssreg.registerStylesheet('invisibles.css', media='screen')
        cssreg.moveResourceAfter('invisibles.css', 'navtree.css')
        out.append("Added invisibles.css to the registry")
    if 'forms.css' not in stylesheet_ids:
        cssreg.registerStylesheet('forms.css', media='screen')
        cssreg.moveResourceAfter('forms.css', 'invisibles.css')
        out.append("Added forms.css to the registry")

def updateActionsI18NDomain(portal, out):
    actions = portal.portal_actions.listActions()
    domainless_actions = [a for a in actions if not a.i18n_domain]
    for action in domainless_actions:
        action.i18n_domain = 'plone'

def updateFTII18NDomain(portal, out):
    types = portal.portal_types.listTypeInfo()
    domainless_types = [fti for fti in types if not fti.i18n_domain]
    for fti in domainless_types:
        fti.i18n_domain = 'plone'
