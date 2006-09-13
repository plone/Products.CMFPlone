from plone.portlets.interfaces import IPortletManager, IPlacelessPortletManager

class IColumn(IPortletManager):
    """Common base class for left and right columns.
    
    Register a portlet for IColumn if it is applicable to regular columns
    but not to the dashboard.
    """

class ILeftColumn(IColumn):
    """The left column.
    
    Normally, you will register portlets for IColumn instead.
    """

class IRightColumn(IColumn):
    """The right column
    
    Normally, you will register portlets for IColumn instead.
    """
    
class IDashboard(IPlacelessPortletManager):
    """The personal dashboard.
    
    Register a portlet for IDashboard if it is applicable to the dashboard
    only.
    """