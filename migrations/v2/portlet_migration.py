from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Acquisition import aq_base

__author__ = 'DannyB (ender)'

conversions={'here/about_slot/macros/aboutBox':'',
      'here/calendar_slot/macros/calendarBox':'here/portlet_calendar/macros/portlet',
      'here/events_slot/macros/eventsBox':'here/portlet_events/macros/portlet',
      'here/favorites_slot/macros/favoritesBox':'here/portlet_favorites/macros/portlet',
      'here/language_slot/macros/languageBox':'here/portlet_language/macros/portlet',
      'here/login_slot/macros/loginBox':'here/portlet_login/macros/portlet',
      'here/navigation_tree_slot/macros/navigationBox':'here/portlet_navigation/macros/portlet',
      'here/news_slot/macros/newsBox':'here/portlet_news/macros/portlet',
      'here/recently_published_slot/macros/recentlyPublishedBox':'here/recently_published_slot/macros/portlet',
      'here/related_slot/macros/relatedBox':'here/portlet_related/macros/portlet',
      'here/workflow_review_slot/macros/review_box':'here/portlet_review/macros/portlet'}

def upgradeSlots2Portlets(portal):
    # traverse all folderish objects and do:
    # rename slots in these properties use the conversion list above

    # handle current obj first
    processObject(aq_base(portal))
    processFolderish(portal)

def processFolderish(folder):
    for obj in folder.contentValues():
        unwrapped = aq_base(obj)
        # avoid max recursion depth error
        if unwrapped.isPrincipiaFolderish and \
          not unwrapped.meta_type == "CMF Collector":
            processObject(unwrapped)
            processFolderish(obj)

def processObject(obj):
    left = getattr(obj, 'left_slots', None)
    if left:
        new=renameEntries(left)
        obj.left_slots=tuple(new)
    right = getattr(obj, 'right_slots', None)
    if right:
        new=renameEntries(right)
        obj.right_slots=tuple(new)

def renameEntries(lines):
    new=[]
    for line in lines:
        if conversions.has_key(line):
            if conversions[line]!='':
                new.append(conversions[line])
        else:
            #retain the line
            new.append(line)
    return new
