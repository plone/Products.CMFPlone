import string
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions as CMFCorePermissions

def two11_two12(portal):
    """2.1.1 -> 2.1.2
    """
    out = []

    # Remove plone_3rdParty\CMFTopic from skin layers
    removeCMFTopicSkinLayer(portal, out)
    addRenameObjectButton(portal, out)

    # add se-highlight.js (plone_3rdParty) to ResourceRegistries
    addSEHighLightJS(portal, out)
    
    # Don't let Discussion item have a workflow
    removeDiscussionItemWorkflow(portal, out)

    return out


def removeCMFTopicSkinLayer(portal, out):
    """Removes plone_3rdParty\CMFTopic layer from all skins."""

    st = getToolByName(portal, 'portal_skins', None)
    if st is not None:
        old = 'plone_3rdParty/CMFTopic'
        skins = st.getSkinSelections()
        for skin in skins:
            path = st.getSkinPath(skin)
            path = map(string.strip, string.split(path,','))
            if old in path:
                path.remove(old)
            st.addSkinSelection(skin, ','.join(path))
        out.append("Removed plone_3rdParty\CMFTopic layer from all skins.")


def addRenameObjectButton(portal,out):
    """Add the missing rename action for renaming single content items.
    """
    
    ACTIONS = (
        {'id'        : 'rename',
         'name'      : 'Rename',
         'action'    : 'python:"%s/object_rename"%(object.isDefaultPageInFolder() and object.getParentNode().absolute_url() or object_url)',
         'condition' : 'python:portal.portal_membership.checkPermission("Delete objects", object.aq_inner.getParentNode()) and portal.portal_membership.checkPermission("Copy or Move", object) and portal.portal_membership.checkPermission("Add portal content", object) and object is not portal and not (object.isDefaultPageInFolder() and object.getParentNode() is portal)',
         'permission': CMFCorePermissions.AddPortalContent,
         'category'  : 'object_buttons',
        },)

    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        # update/add actions
        for newaction in ACTIONS:
            idx = 0
            for action in actionsTool.listActions():
                # if action exists, remove and re-add
                if action.getId() == newaction['id'] \
                        and action.getCategory() == newaction['category']:
                    actionsTool.deleteActions((idx,))
                    out.append("Removed '%s' contentmenu action from actions tool." % newaction['name'])
                    break
                idx += 1

            actionsTool.addAction(newaction['id'],
                name=newaction['name'],
                action=newaction['action'],
                condition=newaction['condition'],
                permission=newaction['permission'],
                category=newaction['category'],
                visible=1)

            out.append("Added '%s' contentmenu action to actions tool." % newaction['name'])

def addSEHighLightJS(portal, out):
    """Add se-highlight.js (plone_3rdParty) to ResourceRegistries.
    """
    jsreg = getToolByName(portal, 'portal_javascripts', None)
    script = 'se-highlight.js'
    if jsreg is not None:
        script_ids = jsreg.getResourceIds()
        # Failsafe: first make sure the stylesheet doesn't exist in the list
        if script not in script_ids:
            jsreg.registerScript(script)
            try:
                jsreg.moveResourceAfter(script, 'highlightsearchterms.js')
            except ValueError:
                # put it at the bottom of the stack
                jsreg.moveResourceToBottom(script)
            out.append("Added " + script + " to portal_javascipt")

def removeDiscussionItemWorkflow(portal, out):
    """Discussion Item should not have a workflow associated with it, since
    it may then have permissions out-of-sync with the parent.
    """
    wftool = getToolByName(portal, 'portal_workflow', None)
    if wftool is not None:
        wftool.setChainForPortalTypes(('Discussion Item',), ())
        out.append("Removing workflow from Discussion Item")