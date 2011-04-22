from zope.interface import Interface


class IInterfaceInformation(Interface):
    """A view that gives information about interfaces provided by its context
    """

    def provides(dotted_name):
        """Given an interface dotted name, determine if the context provides
        this interface.
        """

    def class_provides(dotted_name):
        """Given an interface dotted name, determine if the context's class
        provides this interface.
        """


class ILayoutPolicy(Interface):
    """A view that gives access to various layout related functions.
    """

    def mark_view(view):
        """Adds a marker interface to the view if it is "the" view for the
        context May only be called from a template.
        """

    def hide_columns(column_left, column_right):
        """Returns a CSS class matching the current column status.
        """

    def have_portlets(manager_name, view=None):
        """Determine whether a column should be shown. The left column is called
        plone.leftcolumn; the right column is called plone.rightcolumn.
        """

    def icons_visible():
        """Returns True if icons should be shown or False otherwise.
        """

    def getIcon(item):
        """Returns an object which implements the IContentIcon interface and
        provides the informations necessary to render an icon. The item
        parameter needs to be adaptable to IContentIcon. Icons can be disabled
        globally or just for anonymous users with the icon_visibility property
        in site_properties.
        """

    def renderBase():
        """Returns the current URL to be used in the base tag.
        """

    def bodyClass(template, view):
        """Returns the CSS class to be used on the body tag.
        """


class ITools(Interface):
    """A view that gives access to common tools
    """

    def actions():
        """The portal_actions tool
        """

    def catalog():
        """The portal_catalog tool
        """

    def membership():
        """The portal_membership tool
        """

    def properties():
        """The portal_properties tool
        """

    def syndication():
        """The portal_syndication tool
        """

    def types():
        """The portal_types tool
        """

    def url():
        """The portal_url tool"""

    def workflow():
        """The portal_workflow tool"""


class IPortalState(Interface):
    """A view that gives access to the current state of the portal
    """

    def portal():
        """The portal object
        """

    def portal_title():
        """The title of the portal object
        """

    def portal_url():
        """The URL of the portal object
        """

    def navigation_root():
        """The navigation root object
        """

    def navigation_root_title():
        """The title of the navigation root object
        """

    def navigation_root_path():
        """ path of the navigation root
        """

    def navigation_root_url():
        """The URL of the navigation root
        """

    def default_language():
        """The default language in the portal
        """

    def language():
        """The current language
        """

    def locale():
        """Get the current locale
        """

    def is_rtl():
        """Whether or not the portal is being viewed in an RTL language
        """

    def member():
        """The current authenticated member
        """

    def anonymous():
        """Whether or not the current member is Anonymous
        """

    def friendly_types():
        """Get a list of portal types considered "end user" types
        """


class IContextState(Interface):
    """A view that gives access to the state of the current context
    """

    def current_page_url():
        """The URL to the current page, including template and query string.
        """

    def current_base_url():
        """The current "actual" URL from the request, excluding the query
        string.
        """

    def canonical_object():
        """The current "canonical" object.

        That is, the current object unless this object is the default page
        in its folder, in which case the folder is returned.
        """

    def canonical_object_url():
        """The URL to the current "canonical" object.

        That is, the current object unless this object is the default page
        in its folder, in which case the folder is returned.
        """

    def view_url():
        """URL to use for viewing

        Files and Images get downloaded when they are directly
        called, instead of with /view appended.  We want to avoid that.
        """

    def view_template_id():
        """The id of the view template of the context
        """

    def is_view_template():
        """Return True if the currentl URL (in the request) refers to the
        standard "view" of the context (i.e. the "view" tab).
        """

    def object_url():
        """The URL of the current object
        """

    def object_title():
        """The prettified title of the current object
        """

    def workflow_state():
        """The workflow state of the current object
        """

    def parent():
        """The direct parent of the current object
        """

    def folder():
        """The current canonical folder
        """

    def is_folderish():
        """True if this is a folderish object, structural or not
        """

    def is_structural_folder():
        """True if this is a structural folder
        """

    def is_default_page():
        """True if this is the default page of its folder
        """

    def is_portal_root():
        """True if this is the portal or the default page in the portal
        """

    def is_editable():
        """Whether or not the current object is editable
        """

    def is_locked():
        """Whether or not the current object is locked
        """

    def actions(category):
        """The filtered actions in the context. You can restrict the actions
        to just one category.
        """

    def portlet_assignable():
        """Whether or not the context is capable of having locally assigned
        portlets.
        """


class IViewView(Interface):
    """Marker interface which specifies that the current view is, in fact,
    a canonical "view" of the object, e.g. what may go on the "view" tab.
    """
