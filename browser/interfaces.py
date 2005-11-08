from zope.interface import Interface


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
        """Returns 5 most recently published News Items in reverse chronological order"""

    def all_news_link():
        """Returns URL, relative to the portal, of a page that display all published News Items"""


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


class IPlone(Interface):
    """ """

    def globals():
        """ """

    def utool():
        """ """

    def portal():
        """ """

    def portal_url():
        """ """

    def mtool():
        """ """

    def gtool():
        """ """

    def atool():
        """ """

    def aitool():
        """ """

    def putils():
        """ """

    def wtool():
        """ """

    def ifacetool():
        """ """

    def syntool():
        """ """

    def portal_title():
        """ """

    def object_title():
        """ """

    def member():
        """ """

    def checkPermission():
        """ """

    def membersfolder():
        """ """

    def isAnon():
        """ """

    def actions():
        """ """

    def keyed_actions():
        """ """

    def user_actions():
        """ """

    def workflow_actions():
        """ """

    def folder_actions():
        """ """

    def global_actions():
        """ """

    def portal_tabs():
        """ """

    def wf_state():
        """ """

    def portal_properties():
        """ """

    def site_properties():
        """ """

    def ztu():
        """ """

    def wf_actions():
        """ """

    def isFolderish():
        """ """

    def template_id():
        """ """

    def slots_mapping():
        """ """

    def Iterator():
        """ """

    def tabindex():
        """ """

    def here_url():
        """ """

    def sl():
        """ """

    def sr():
        """ """

    def hidecolumns():
        """ """

    def default_language():
        """ """

    def language():
        """ """

    def is_editable():
        """ """

    def isEditable():
        """ """

    def lockable():
        """ """

    def isLocked():
        """ """

    def isRTL():
        """ """

    def visible_ids():
        """ """

    def current_page_url():
        """ """
