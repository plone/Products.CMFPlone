from zope.interface import Interface

class INewsPortlet(Interface):
    """ """

    def news():
        """ """

    def news_listing():
        """ """

class INavigationPortlet(Interface):
    """ """

    def includeTop():
        """ """

    def createNavTree():
        """ """

    def isPortalOrDefaultChild():
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


class IPloneGlobals(Interface):
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
    
