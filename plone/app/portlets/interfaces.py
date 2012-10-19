from zope.interface import Interface

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPlacelessPortletManager
from plone.portlets.interfaces import IPortletRenderer


class IPortletTypeInterface(Interface):
    """IInterface for portlet type interfaces. The portlet ZCML directive
    will register the portlet type interface as a utility providing this
    interface, with a name corresponding to the addview of the portlet.
    """


class IUserPortletAssignmentMapping(IPortletAssignmentMapping):
    """A portlet assignment mapping that's user-specific
    """


class IGroupDashboardPortletAssignmentMapping(IPortletAssignmentMapping):
    """Group portlets storage. Has its own security checker.
    """


class IPortletPermissionChecker(Interface):
    """An adapter for an assignment manager, which can check whether the
    current user is allowed to manipulate portlets in this mapping.
    """

    def __call__():
        """Check the adapted assignment manager. Will raise Unathorized if
        something fishy is going on.
        """


class IDefaultPortletManager(IPortletManager):
    """Default registration for portlets
    """


class IColumn(IDefaultPortletManager):
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


class IDashboard(IDefaultPortletManager, IPlacelessPortletManager):
    """Common base class for dashboard columns

    Register a portlet for IDashboard if it is applicable to the dashboard
    only.
    """


class IDeferredPortletRenderer(IPortletRenderer):
    """Provide refresh and dynamic loading functionality"""

    def deferred_update():
        """refresh portlet data on KSS events (and only then)

        this is similar to update() but it is only called from a KSS action
        and thus can be used to do long computing/retrieval only on loading
        the portlet via KSS but not in the initial page load.
        """

    def render_full():
        """method for rendering the full version of the portlet

        this is usually the one called via KSS events
        """

    def render_preload():
        """method for rendering the portlet in preloading state

        this usually just contains a class to which an KSS event is bound
        """

    def initialized():
        """return whether the portlet is initialized or not

        depending on this the render() method chooses whether to render the
        preload or full version (if initialized==True).
        """


class IDefaultDashboard(Interface):
    """Define an adapter from the user/principal type (by default, this is
    Products.PluggableAuthService.interfaces.authservice.IBasicUser) to
    this interface and implement __call__ to return a mapping of dashboard
    settings. When a new user is created, this adapter will be invoked to
    build a default dashboard.
    """

    def __call__(self):
        """Create and return dashboard portlet assignments. Should be a
        mapping of dashboard column names ('plone.dashboard1',
        'plone.dashboard2', 'plone.dashboard3' and/or 'plone.dashboard4')
        and a list of portlet assignmen instances.
        """
