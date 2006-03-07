from zope.interface import Interface, Attribute


class IDefaultPage(Interface):

    def isDefaultPage(obj):
        """Finds out if the given obj is the default page for the
        adapted object.
        """

    def getDefaultPage():
        """Returns the id of the default page for the adapted object.
        """


class INavigationBreadcrumbs(Interface):

    def breadcrumbs():
        """Breadcrumbs for Navigation.
        """

class INavigationTabs(Interface):

    def topLevelTabs(actions=None):
        """Top level tabs
        """

class INavigationTree(Interface):

    def navigationTree():
        """Navigation Tree
        """

class INavigationStructure(INavigationBreadcrumbs,
                           INavigationTabs,
                           INavigationTree):
    """Navigation Structure
    """

class INavigationRoot(Interface):
    """A marker interface for signaling the navigation root.
    """


class INavigationPortlet(Interface):
    """ """

    def includeTop():
        """ """

    def createNavTree():
        """ """

    def isPortalOrDefaultChild():
        """ """


class INewsPortlet(Interface):
    """Interface for portlet to display recent news items"""

    def published_news_items():
        """Returns 5 most recently published News Items in reverse
           chronological order
        """

    def all_news_link():
        """Returns URL, relative to the portal, of a page that display all
           published News Items
        """


class IEventsPortlet(Interface):
    """Interface for portlet to display recent news items"""

    def published_events():
        """Returns 5 most recently published News Items in reverse
           chronological order
        """

    def all_events_link():
        """Returns URL, relative to the portal, of a page that display all
           published News Items
        """

    def prev_events_link():
        """Returns URL, relative to the portal, of a page that display all
           past events.
        """


class IRecentPortlet(Interface):
    """ """

    def results():
        """ """


class ICalendarPortlet(Interface):

    def DateTime():
        """ """

    def current():
        """ """

    def current_day():
        """ """

    def nextYearMax():
        """ """

    def prevYearMin():
        """ """

    def year():
        """ """

    def month():
        """ """

    def prevMonthTime():
        """ """

    def nextMonthTime():
        """ """

    def weeks():
        """ """

    def getYearAndMonthToDisplay():
        """ """

    def getPreviousMonth(month, year):
        """ """

    def getNextMonth(month, year):
        """ """


class ISitemapView(Interface):
    """ """

    def createSitemap():
        """ """


class IPlone(Interface):
    """ """


    def globalize():
        """ A method which puts all of the following view attributes into the
            globals of the current tal expression context (plus the
            toLocalizedTime method):

    portal = Attribute("The portal object itself")

    portal_url = Attribute("The portal url")

    mtool = Attribute("The portal_membership tool")

    putils = Attribute("The plone_utils tool (PloneTool)")

    wtool = Attribute("The portal_workflow tool")

    ifacetool = Attribute("The portal_interface tool")

    syntool = Attribute("The portal_syndication tool")

    portal_title = Attribute("The title of the portal")

    object_title = Attribute("The title of the current object (context)")

    member = Attribute("The member object for the authenticated user in "
                       "context")

    checkPermission = Attribute("The checkPermission method of the membership"
                                " tool")

    membersfolder = Attribute("The portal's Members folder")

    isAnon = Attribute("Boolean indicating whether the current user is "
                       "anonymous")

    actions = Attribute("The result of listFilteredActionsFor(context) in the "
                        "portal_actions tool")

    keyed_actions = Attribute("A mapping of action categories to action ids "
                              "to action information: "
                              "mapping[cat][id] == actioninfo")

    user_actions = Attribute("Actions in the user category")

    workflow_actions = Attribute("Actions in the workflow category")

    folder_actions = Attribute("Actions in the folder category")

    global_actions = Attribute("Actions in the global category")

    portal_tabs = Attribute("The actions for the portal tabs")

    wf_state = Attribute("The review_state of the current object")

    portal_properties = Attribute("The portal_properties tool")

    site_properties = Attribute("The site_properties tool")

    ztu = Attribute("The ZTUtils module")

    isFolderish = Attribute("A boolean indicating whether the object is "
                            "folderish")

    slots_mapping = Attribute("A mapping containing a list of macros or "
                              "expressions for each slot")

    here_url = Attribute("The url of the current object")

    sl = Attribute("The elements in the left slot")

    sr = Attribute("The elements in the right slot")

    default_language = Attribute("The default language of the portal")

    language = Attribute("The language of the current request or context.")

    is_editable = Attribute("A boolean indicating if the current user has "
                            " edit permissions in this context")

    isLocked = Attribute("A boolean indicating that the object is webdav "
                         "locked")

    isRTL = Attribute("A boolean indicating that the current language is a "
                      "right-to-left language.")

    visible_ids = Attribute("A boolean indicating whether to show object ids "
                            "to the current user")

    current_page_url = Attribute("The full url with query string")

    isContextDefaultPage = Attribure("Boolean idicating that the context is "
                                     "the default page of its parent folder.")

    isStructuralFolder = Attribute("Boolean indicating that the context is a "
                                   "'Structural Folder'.")

    # BBB: deprecated elements
    utool = Attribute("The portal_url tool")
    portal_object = Attribute("A deprecated spelling of portal")
    atool = Attribute("The portal_actions tool")
    aitool = Attribute("The portal_actionicons tool")
    gtool = Attribute("The portal_groups tool")
    gdtool = Attribute("The portal_groupdata tool")
    wf_actions = Attribute("A deprecated variant of workflow_actions")
    hidecolumns = Attribute("The css class to use for the column container"
                            "which determines which columns to show")
    isEditable = Attribute("A deprecated spelling of is_editable")
    lockable = Attribute("A boolean indicating that the object capable of"
                             " being webdav locked")
    """

    def getCurrentUrl():
        """ Returns the actual url plus the query string. """

    def keyFilteredActions(actions=None):
        """ Returns a mapping of action categories to action ids to action
            information: mapping[cat][id] == actioninfo

            Optionally takes an action list, if ommitted it will be calculated
        """

    def visibleIdsEnabled():
        """Determines whether to show object ids based on portal and user
           settings.
        """

    def isRightToLeft(domain):
        """Is the currently selected language a right to left language"""

    def toLocalizedTime(time, long_format=None):
        """ The time parameter must be either a string that is suitable for
            initializing a DateTime or a DateTime object. Returns a localized
            string.
        """

    def isDefaultPageInFolder():
        """ Returns a boolean indicating whether the current context is the
            default page of its parent folder.
        """

    def isStructuralFolder():
        """Checks if a given object is a "structural folder".

        That is, a folderish item which does not explicitly implement
        INonStructuralFolder to declare that it doesn't wish to be treated
        as a folder by the navtree, the tab generation etc.
        """

    def hide_columns(self, column_left, column_right):
        """ Returns the CSS class used by the page layout hide empty
            portlet columns.
        """
