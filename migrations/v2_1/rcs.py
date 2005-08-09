from alphas import reindexCatalog, indexMembersFolder, indexNewsFolder, \
                    indexEventsFolder, addIs_FolderishMetadata
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions


def rc1_rc2(portal):
    """2.1-beta1 -> 2.1-beta2
    """
    out = []
    reindex = 0

    # Re-add metadata column to indicate whether an object is folderish
    reindex += addIs_FolderishMetadata(portal, out)

    # Change views available on foderish objects
    changeAvailableViewsForFolders(portal, out)

    # Enable syndication on all topics during migraiton
    enableSyndicationOnTopics(portal, out)

    # Disable syndication object action
    disableSyndicationAction(portal, out)

    # Change RSS action title to be more accurate
    alterRSSActionTitle(portal, out)

    # FIXME: *Must* be called after reindexCatalog.
    # In tests, reindexing loses the folders for some reason...

    # Rebuild catalog
    if reindex:
        reindexCatalog(portal, out)

    # Make sure the Members folder is cataloged
    indexMembersFolder(portal, out)

    # Make sure the News folder is cataloged
    indexNewsFolder(portal, out)

    # Make sure the Events folder is cataloged
    indexEventsFolder(portal, out)

    return out


def changeAvailableViewsForFolders(portal, out):
    """Add view templates to the folderish types"""
    FOLDER_TYPES = ['Folder','Large Plone Folder', 'Topic']
    FOLDER_VIEWS = ['folder_listing', 'atct_album_view']

    types_tool = getToolByName(portal, 'portal_types', None)
    if types_tool is not None:
        for type_name in FOLDER_TYPES:
            fti = getattr(types_tool, type_name, None)
            if fti is not None:
                views = FOLDER_VIEWS
                if type_name == 'Topic':
                    views = ['atct_topic_view']+views
                fti.manage_changeProperties(view_methods=views)
                out.append("Added new view templates to %s FTI."%type_name)

def enableSyndicationOnTopics(portal, out):
    syn = getToolByName(portal, 'portal_syndication', None)
    if syn is not None:
        enabled = syn.isSiteSyndicationAllowed()
        # We must enable syndication for the site to enable it on objects
        # otherwise we get a nasty string exception from CMFDefault
        syn.editProperties(isAllowed=True)
        cat = getToolByName(portal, 'portal_catalog', None)
        if cat is not None:
            topics = cat(portal_type='Topic')
            for b in topics:
                topic = b.getObject()
                # If syndication is already enabled then another nasty string
                # exception gets raised in CMFDefault
                if topic is not None and not syn.isSyndicationAllowed(topic):
                    syn.enableSyndication(topic)
                    out.append('Enabled syndication on %s'%b.getPath())
        # Reset site syndication to default state
        syn.editProperties(isAllowed=enabled)

def disableSyndicationAction(portal, out):
    """ Disable the syndication action
    """
    syn = getToolByName(portal, 'portal_syndication', None)
    if syn is not None:
        new_actions = syn._cloneActions()
        for action in new_actions:
            if action.getId() == 'syndication' and \
                                     action.category in ['folder', 'object']:
                action.visible = 0
        syn._actions = new_actions
        out.append("Disabled 'syndication' object action.")

def alterRSSActionTitle(portal, out):
    """ Change the RSS action to give it a more appropriate title
    """
    newaction = {'id'        : 'rss',
                  'name'      : 'RSS feed of this listing',
                  'action'    : 'string:$object_url/RSS',
                  'condition' : 'python:portal.portal_syndication.isSyndicationAllowed(object)',
                  'permission': CMFCorePermissions.View,
                  'category': 'document_actions',
                }
    exists = False
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        new_actions = actionsTool._cloneActions()
        for action in new_actions:
            if action.getId() == 'rss' and action.category == newaction['category']:
                exists = True
                if 'contents' in action.title:
                    action.title = newaction['name']
        if exists:
            actionsTool._actions = new_actions
            out.append("Changed RSS action title")
        else:
            actionsTool.addAction(newaction['id'],
                    name=newaction['name'],
                    action=newaction['action'],
                    condition=newaction['condition'],
                    permission=newaction['permission'],
                    category=newaction['category'],
                    visible=1)
            out.append("Added missing RSS action")
