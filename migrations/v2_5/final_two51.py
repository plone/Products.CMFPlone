from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.UnicodeSplitter import Splitter, CaseNormalizer
from Products.CMFPlone.migrations.v2_1.alphas import reindexCatalog, \
     indexMembersFolder


def final_two51(portal):
    """2.5-final -> 2.5.1
    """
    out = []
    removePloneCssFromRR(portal, out)

    # add event_registration.js
    addEventRegistrationJS(portal, out)

    # Repair plone_lexicon pipeline
    fixupPloneLexicon(portal, out)

    # Make object delete action use confirmation form
    fixObjDeleteAction(portal, out)

    # Required for #5569 (is_folderish needs reindexing) and #5231 (all text
    # indices need to be reindexed so they are split properly)
    reindexCatalog(portal, out)

    # FIXME: *Must* be called after reindexCatalog.
    # In tests, reindexing loses the folders for some reason...

    # Make sure the Members folder is cataloged
    indexMembersFolder(portal, out)

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
    newaction = { 'id'         : 'delete',
                  'name'       : 'Delete',
                  'action'     : 'string:${globals_view/getCurrentObjectUrl}/delete_confirmation',
                  'condition'  : 'python:checkPermission(&quot;Delete objects&quot;, globals_view.getParentObject()) and not globals_view.isPortalOrPortalDefaultPage()',
                  'permission' : 'Delete objects',
                  'category'   : 'object_buttons',
                }
    exists = False
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        new_actions = actionsTool._cloneActions()
        for action in new_actions:
            if action.getId() == newaction['id'] and action.category == newaction['category']:
                exists = True
                action.action = Expression(text=newaction['action'])
                out.append('Modified existing object delete action')
        if exists:
            actionsTool._actions = new_actions
        else:
            actionsTool.addAction(newaction['id'],
                    name=newaction['name'],
                    action=newaction['action'],
                    condition=newaction['condition'],
                    permission=newaction['permission'],
                    category=newaction['category'],
                    visible=1)
            out.append("Added missing object delete action")
