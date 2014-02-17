from zope.interface import Interface

import zope.deferredimport

# This is used as a persistent marker interface, we need to provide an upgrade
# step to update the class reference before removing it.
zope.deferredimport.deprecated(
    "It has been moved to plone.app.layout.navigation.interfaces. "
    "This alias will be removed in Plone 5.0",
    INavigationRoot='plone.app.layout.navigation.interfaces:INavigationRoot',
    )


class INavigationBreadcrumbs(Interface):

    def breadcrumbs():
        """Breadcrumbs for Navigation.
        """


class INavigationTabs(Interface):

    def topLevelTabs(actions=None, category='portal_tabs'):
        """Top level tabs
        """


class INavigationTree(Interface):

    def navigationTreeRootPath():
        """Get the path to the root of the navigation tree
        """

    def navigationTree():
        """Navigation tree
        """


class ISiteMap(Interface):

    def siteMap():
        """Site map
        """


class INavigationPortlet(Interface):
    """Interface for portlet to display navigation tree"""

    def title():
        """The title of the navigation portlet (may be '' to fall back on default)"""

    def display():
        """Whether or not the navtree should be displayed"""

    def includeTop():
        """Whether or not to include the root element in the tree"""

    def navigationRoot():
        """Get the root object"""

    def rootTypeName():
        """Get a normalized content type name for the root object"""

    def createNavTree():
        """Build the actual tree"""

    def isPortalOrDefaultChild():
        """Determine if the context is the portal or a default-document"""


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
    """Interface for portlet to display recently modified items"""

    def results():
        """Get the list of recently modified items"""


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

    def showStates():
        """ """

    def showPrevMonth():
        """ """

    def showNextMonth():
        """ """

    def getYearAndMonthToDisplay():
        """ """

    def getPreviousMonth(month, year):
        """ """

    def getNextMonth(month, year):
        """ """

    def getWeekdays(self):
        """Returns a list of Messages for the weekday names."""

    def getEnglishMonthName(self, month):
        """Returns the English month name."""

    def getMonthName(self, month):
        """Returns the month name as a Message."""

    def isToday(self, day):
        """Returns True if the given day and the current month and year equals
           today, otherwise False.
        """


class ISitemapView(Interface):
    """Interface to the view that creates a site map"""

    def createSiteMap():
        """Create the site map data structure"""


class IPlone(Interface):
    """ """

    def getCurrentUrl():
        """ Returns the actual url plus the query string. """

    def visibleIdsEnabled():
        """Determines whether to show object ids based on portal and user
           settings.
        """

    def uniqueItemIndex(pos=0):
        """Return an index iterator."""

    def toLocalizedTime(time, long_format=None, time_only=None):
        """ The time parameter must be either a string that is suitable for
            initializing a DateTime or a DateTime object. Returns a localized
            string.
        """

    def toLocalizedSize(size):
        """ Convert an integer to a localized size string
        3322 -> 3KB in english, 3Ko in french
        """

    def normalizeString(text):
        """Normalizes a title to an id.
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

    def navigationRootPath():
        """Get the current navigation root path
        """

    def navigationRootUrl():
        """Get the url to the current navigation root
        """

    def getParentObject():
        """Returns the parent of the current object, equivalent to
           aq_inner(aq_parent(context)), or context.aq_inner.getParentNode()
        """

    def getCurrentFolder():
        """If the context is the default page of a folder or is not itself a
           folder, the parent is returned, otherwise the object itself is
           returned.  This is useful for providing a context for methods
           which wish to act on what is considered the current folder in the
           ui.
        """

    def getCurrentFolderUrl():
        """Returns the URL of the current folder as determined by
           self.getCurrentFolder(), used heavily in actions.
        """

    def getCurrentObjectUrl():
        """Returns the URL of the current object unless that object is a
           folder default page, in which case it returns the parent.
        """

    def isFolderOrFolderDefaultPage():
        """Returns true only if the current object is either a folder (as
           determined by isStructuralFolder) or the default page in context.
        """

    def isPortalOrPortalDefaultPage():
        """Returns true only if the current object is either the portal object
           or the default page of the portal.
        """

    def getViewTemplateId():
        """Returns the template Id corresponding to the default view method of
           the context object.
        """

    def showEditableBorder():
        """Returns true if the editable border should be shown
        """

    def displayContentsTab():
        """Returns true if the contents tab should be displayed in the current
           context.  Evaluates whether the object is a folder or the default
           page of a folder, and checks if the user has relevant permissions.
        """

    def getIcon(item):
        """Returns an object which implements the IContentIcon interface and
           provides the informations necessary to render an icon.
           The item parameter needs to be adaptable to IContentIcon.
           Icons can be disabled globally or just for anonymous users with
           the icon_visibility property in site_properties."""

    def cropText(text, length, ellipsis):
        """ Crop text on a word boundary """

    def have_portlets(manager_name, view=None):
        """Determine whether a column should be shown."""

    def mark_view(view):
        """ Adds a marker interface to the view if it is "the" view for the context
            May only be called from a template.
        """

    def site_encoding():
        """ returns site encoding """

    def bodyClass(template, view):
        """ returns template or view name to mark body tag with
            template-${template_id} CSS class
        """
