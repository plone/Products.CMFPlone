from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression


def alpha2_beta1(portal):
    """2.1-alpha2 -> 2.1-beta1
    """
    out = []

    #Make object paste action work with all default pages.
    fixObjectPasteActionForDefaultPages(portal, out)

    # Make batch action a toggle by using a pair of actions
    fixBatchActionToggle(portal, out)

    # Update the 'my folder' action to not use folder_contents
    fixMyFolderAction(portal, out)

    # Bring ploneRTL back to the nearly-top of the stack
    reorderStylesheets(portal, out)

    # Grant Access inactive portal content to Owner
    allowOwnerToAccessInactiveContent(portal, out)

    # Add criteria to News and Events topics to restrict to published
    restrictNewsTopicToPublished(portal, out)
    restrictEventsTopicToPublished(portal, out)
    
    return out


def fixObjectPasteActionForDefaultPages(portal, out):
    """ Change the plone_setup action so that its title is Site Setup.
    """
    newaction =  {'id'        : 'paste',
                  'name'      : 'Paste',
                  'action'    : 'python:"%s/object_paste"%(object.isDefaultPageInFolder() and object.getParentNode().absolute_url() or object_url)',
                  'condition' : 'folder/cb_dataValid',
                  'permission': CMFCorePermissions.View,
                  'category': 'object_buttons',
                 }
    exists = False
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        new_actions = actionsTool._cloneActions()
        for action in new_actions:
            if action.getId() == newaction['id'] and action.category == newaction['category']:
                exists = True
                action.setActionExpression(Expression(newaction['action']))
                out.append('Modified existing object paste action for folderish default pages')
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
            out.append("Added missing object paste action")
            
def fixBatchActionToggle(portal, out):
    """Fix batch actions so as to function as a toggle
    """
    ACTIONS = (
        {'id'        : 'batch',
         'name'      : 'Contents',
         'action'    : "python:((object.isDefaultPageInFolder() and object.getParentNode().absolute_url()) or folder_url)+'/folder_contents'",
         'condition' : "python:folder.displayContentsTab() and object.REQUEST['ACTUAL_URL'] != object.absolute_url() + '/folder_contents'",
         'permission': CMFCorePermissions.View,
         'category'  : 'batch',
        },
        {'id'        : 'nobatch',
         'name'      : 'Default view',
         'action'    : "string:${folder_url}/view",
         'condition' : "python:folder.displayContentsTab() and object.REQUEST['ACTUAL_URL'] == object.absolute_url() + '/folder_contents'",
         'permission': CMFCorePermissions.View,
         'category'  : 'batch',
        },
    )

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

def fixMyFolderAction(portal, out):
    """Fix my folder action to point to folder w/o folder_contents
    """
    actionsTool = getToolByName(portal, 'portal_membership', None)
    if actionsTool is not None:
        for action in actionsTool.listActions():
            if action.getId() == 'mystuff' and action.getCategory() == 'user':
                action.setActionExpression(Expression('string:${portal/portal_membership/getHomeUrl}'))
                out.append("Made the 'mystuff' action point to folder listing instead of folder_contents")
                break

def reorderStylesheets(portal, out):
    """ Fix the position of the ploneRTL and member.css stylesheet

    After the 'alphas' migration, ploneRTL was at the bottom of the
    pile - it should be near the top in order to overwrite common
    plone stuff (which is left-to-right) for right-to-left (hebrew,
    arabic, etc.) usage.

    ploneMember.css breaks some stylesheet-combining order, so we're
    moving it to the bottom of the list.
    """
    qi = getToolByName(portal, 'portal_quickinstaller', None)
    if qi is not None:
        if not qi.isProductInstalled('ResourceRegistries'):
            qi.installProduct('ResourceRegistries', locked=0)
        cssreg = getToolByName(portal, 'portal_css', None)
        if cssreg is not None:
            stylesheet_ids = [item.get('id') for item in cssreg.getResources()]
            # Failsafe: first make sure the two stylesheets exist in the list
            if 'ploneRTL.css' not in stylesheet_ids:
                cssreg.registerStylesheet('ploneRTL.css',
                                           expression="python:object.isRightToLeft(domain='plone')")
            if 'ploneCustom.css' not in stylesheet_ids:
                cssreg.registerStylesheet('ploneCustom.css')
            if 'ploneMember.css' not in stylesheet_ids:
                cssreg.registerStylesheet('ploneMember.css',
                                           expression='not: portal/portal_membership/isAnonymousUser')
            # Now move 'em
            cssreg.moveResourceBefore('ploneRTL.css', 'ploneCustom.css')
            cssreg.moveResourceToTop('ploneMember.css')


def allowOwnerToAccessInactiveContent(portal, out):
    permission = CMFCorePermissions.AccessInactivePortalContent
    cur_perms=portal.permission_settings(permission)[0]
    roles = portal.valid_roles()
    if 'Owner' in roles:
        cur_allowed = [roles[i] for i in range(len(cur_perms['roles'])) if cur_perms['roles'][i]['checked']]
        if 'Owner' not in cur_allowed:
            cur_allowed.append('Owner')
            acquire = cur_perms['acquire'] and 1 or 0
            portal.manage_permission(permission, tuple(cur_allowed),
                                                        acquire=acquire)
            out.append('Cranted "Access inactive portal content" permission to Owner role')


def restrictNewsTopicToPublished(portal, out):
    news = getattr(portal,'news', None)
    topic = getattr(news,'news_topic', None)
    if topic is not None:
        crit = getattr(topic, 'crit__review_state_ATSimpleStringCriterion', None)
        if crit is None:
            state_crit = topic.addCriterion('review_state',
                                                 'ATSimpleStringCriterion')
            state_crit.setValue('published')
            out.append('Added published criterion to news topic.')
        else:
            out.append('News topic already restricted to published.')
    else:
        out.append('News topic view not in place!')


def restrictEventsTopicToPublished(portal, out):
    events = getattr(portal,'events', None)
    topic = getattr(events,'events_topic', None)
    if topic is not None:
        crit = getattr(topic, 'crit__review_state_ATSimpleStringCriterion', None)
        if crit is None:
            state_crit = topic.addCriterion('review_state',
                                                 'ATSimpleStringCriterion')
            state_crit.setValue('published')
            out.append('Added published criterion to events topic.')
        else:
            out.append('Events topic already restricted to published.')
    else:
        out.append('Events topic view not in place!')