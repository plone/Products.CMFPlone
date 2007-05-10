from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.permissions import DeleteObjects
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.UnicodeSplitter import Splitter, CaseNormalizer
from Products.CMFPlone.migrations.v3_0.alphas import migrateOldActions
from Products.CMFPlone.migrations.v3_0.alphas import enableZope3Site
from Products.CMFPlone.migrations.v3_0.alphas import registerToolsAsUtilities


def final_two51(portal):
    """2.5-final -> 2.5.1
    """
    out = []

    # Make the portal a Zope3 site
    enableZope3Site(portal, out)

    # register some tools as utilities
    registerToolsAsUtilities(portal, out)

    removePloneCssFromRR(portal, out)

    # add event_registration.js
    addEventRegistrationJS(portal, out)

    # Repair plone_lexicon pipeline
    fixupPloneLexicon(portal, out)

    # We need to migrate all existing actions to new-style actions first
    migrateOldActions(portal, out)
    # Make object delete action use confirmation form
    fixObjDeleteAction(portal, out)

    # Required for #5569 (is_folderish needs reindexing) and #5231 (all text
    # indices need to be reindexed so they are split properly)
    migtool = getToolByName(portal, 'portal_migration')
    migtool._needRecatalog = True

    return out


def removePloneCssFromRR(portal, out):
    """Removes the redundant, deprecated, and failing plone.css from portal_css.
       It is a python script now and just calls portal_css itself."""
    css_reg = getToolByName(portal, 'portal_css', None)
    if css_reg is not None:
        stylesheet_ids = css_reg.getResourceIds()
        if 'plone.css' in stylesheet_ids:
            css_reg.unregisterResource('plone.css')
            out.append('Unregistered deprecated plone.css')


def addEventRegistrationJS(portal, out):
    """Add event-registration.js to ResourceRegistries.
    """
    jsreg = getToolByName(portal, 'portal_javascripts', None)
    script = 'event-registration.js'
    if jsreg is not None:
        script_ids = jsreg.getResourceIds()
        # Failsafe: first make sure the stylesheet doesn't exist in the list
        if script not in script_ids:
            jsreg.registerScript(script)
            # put it at the top of the stack
            jsreg.moveResourceToTop(script)
            out.append("Added " + script + " to portal_javascipt")


def fixupPloneLexicon(portal, out):
    """Updates the plone_lexicon pipeline with the new splitter
       and case normalizer.
    """
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        if 'plone_lexicon' in catalog.objectIds():
            lexicon = catalog.plone_lexicon
            pipeline = list(lexicon._pipeline)
            if len(pipeline) >= 2:
                if (not isinstance(pipeline[0], Splitter) or
                    not isinstance(pipeline[1], CaseNormalizer)):
                    pipeline[0] = Splitter()
                    pipeline[1] = CaseNormalizer()
                    lexicon._pipeline = tuple(pipeline)
                    # Clear the lexicon
                    from BTrees.OIBTree import OIBTree
                    from BTrees.IOBTree import IOBTree
                    from BTrees.Length import Length
                    lexicon._wids = OIBTree()
                    lexicon._words = IOBTree()
                    lexicon.length = Length()
                    out.append('Updated plone_lexicon pipeline.')


def fixObjDeleteAction(portal, out):
    """Make the delete action use the new confirmation form
    """
    delete = Action('delete',
        title='Delete',
        i18n_domain='plone',
        url_expr='string:${globals_view/getCurrentObjectUrl}/delete_confirmation',
        available_expr='python:checkPermission("Delete objects", globals_view.getParentObject()) and not globals_view.isPortalOrPortalDefaultPage()',
        permissions=(DeleteObjects,),
        visible=True)

    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        category = actionsTool.object_buttons
        for action in category.objectIds():
            # if action exists, remove and re-add
            if action == 'delete':
                category._delObject('delete')
                break

        category['delete'] = delete
        category.moveObjectsToBottom(('delete',))
        category.moveObjectsUp(('delete',))
        out.append("Added/modified delete object_buttons action.")
