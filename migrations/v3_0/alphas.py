from zope.app.component.interfaces import ISite
from zope.component.globalregistry import base
from zope.component.persistentregistry import PersistentComponents

from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.ActionInformation import ActionCategory
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
