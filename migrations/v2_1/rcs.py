from alphas import reindexCatalog, indexMembersFolder, indexNewsFolder, \
                    indexEventsFolder, addIs_FolderishMetadata
from betas import fixContentActionConditions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFPlone.utils import _createObjectByType


def rc1_rc2(portal):
    """2.1-rc1 -> 2.1-rc2
    """
    out = []
    reindex = 0

    # Re-add metadata column to indicate whether an object is folderish
    reindex += addIs_FolderishMetadata(portal, out)

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


def rc2_final(portal):
    """2.1-rc2 -> 2.1-final
    """
    out = []

    # Add an events subtopic for past events
    addPastEventsTopic(portal, out)

    # Add date criteria to limit the events_topic to current events
    addDateCriterionToEventsTopic(portal, out)

    # Make sure we don't get two 'sharing' tabs on the portal root
    fixDuplicatePortalRootSharingAction(portal, out)

    # Redo action changes due to bad override
    fixContentActionConditions(portal, out)

    # Change views available on foderish objects
    changeAvailableViewsForFolders(portal, out)

    return out


def changeAvailableViewsForFolders(portal, out):
    """Add view templates to the folderish types"""
    FOLDER_TYPES = ['Folder','Large Plone Folder', 'Topic']
    FOLDER_VIEWS = ['folder_listing', 'folder_tile_view', 'folder_tabular_view', 'atct_album_view']

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

def addPastEventsTopic(portal, out):
    """Add past events subtopic the events topic"""
    events = getattr(portal ,'events', None)
    events_topic = getattr(events, 'events_topic', None)
    if events_topic is not None and \
                'previous' not in events_topic.objectIds() and \
                getattr(portal,'portal_atct', None) is not None:
        _createObjectByType('Topic', events_topic, id='previous',
                            title='Past Events',
                            description="Events which have already happened.")
        topic = events_topic.previous
        topic.setAcquireCriteria(True)
        sort_crit = topic.addCriterion('start','ATSortCriterion')
        sort_crit.setReversed(True)
        date_crit = topic.addCriterion('start','ATFriendlyDateCriteria')
        # Set date reference to now
        date_crit.setValue(0)
        # Only take events in the past
        date_crit.setDateRange('-') # This is irrelevant when the date is now
        date_crit.setOperation('less')
        out.append('Added Topic for previous events.')

def addDateCriterionToEventsTopic(portal, out):
    """Add past events subtopic the events topic"""
    events = getattr(portal ,'events', None)
    topic = getattr(events, 'events_topic', None)
    if topic is not None and \
                            getattr(portal,'portal_atct', None) is not None:
        if 'crit__start_ATFriendlyDateCriteria' not in topic.objectIds():
            date_crit = topic.addCriterion('start',
                                           'ATFriendlyDateCriteria')
            # Set date reference to now
            date_crit.setValue(0)
            # Only take events in the future
            date_crit.setDateRange('+') # This is irrelevant when the date is now
            date_crit.setOperation('more')
            out.append('Added criterion to limit to current events.')


def fixDuplicatePortalRootSharingAction(portal, out):
    """The 'sharing' action at portal root must be called local_roles"""
    ttool = getToolByName(portal, 'portal_types', None)
    if ttool is not None:
        fti = getattr(ttool, 'Plone Site', None)
        if fti is not None:
            idx = 0
            oldAction = None
            oldIdx = -1
            haveLocalRoles = False
            for action in fti.listActions():
                if action.getId() == 'sharing':
                    oldAction = action
                    oldIdx = idx
                elif action.getId() == 'local_roles':
                    haveLocalRoles = True
                idx += 1
            if oldAction is not None:
                fti.deleteActions((oldIdx,))
                out.append('Deleted sharing action with id "sharing"')
                if not haveLocalRoles:
                    fti.addAction('local_roles',
                                    name=oldAction.Title(),
                                    action=oldAction.getActionExpression(),
                                    condition=oldAction.getCondition(),
                                    permission=oldAction.getPermissions(),
                                    category=oldAction.getCategory(),
                                    visible=oldAction.getVisibility())
                    out.append('Renamed the sharing action to "local_roles"')