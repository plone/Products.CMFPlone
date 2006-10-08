from zope.interface import Interface
from zope.interface import directlyProvides

from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.publisher.interfaces.browser import IBrowserSubMenuItem
from zope.app.publisher.interfaces.browser import IMenuItemType

from zope.contentprovider.interfaces import IContentProvider

class IContentMenuView(IContentProvider):
    """The view that powers the content menu (the green bar at the top of
    the editable border).
    
    This will construct a menu by finding an adapter to IContentMenu.
    """
    
    def available():
        """Determine whether the menu should be displayed at all.
        """
    
    def menu():
        """Create a list of dicts that can be used to render a menu.
        
        The keys in this dict are: title, description, action (a URL), 
        selected (a boolean), icon (a URI), extra (a random payload), and
        submenu 
        """

# The content menu itself - menu items are registered as adapters to this
# interface (this is signalled by marking the interface itself with the
# IInterface IMenuItemType)

class IContentMenuItem(Interface):
    """Special menu item type for Plone's content menu."""

directlyProvides(IContentMenuItem, IMenuItemType)

# The sub-menus - because they require additional logic, each of these will be
# implemented with a separate class. We provide markers here to distinguish
# them, although IBrowserMenu is the primary interface through which they are
# looked up. We also provide markers for the special menu items - see 
# configure.zcml for more details.

# We use the 'extra' field in the menu items for various bits of information
# the view needs to render the menu. 'extra' will be a dict, with the following
# keys, all optional:
#
#   id           :   The id of the menu item, e.g. the id of the type to add or
#                        the workflow transition
#   state        :   The current state of the item
#   stateTitle   :   The title of the state - to be displayed after the main
#                        item title
#   class        :   A CSS class to apply
#   separator    :   True if the item should be preceded by a separator
#   hideChildren :   True if the item's children should not be rendered


class IActionsSubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the actions menu.
    """

class IActionsMenu(IBrowserMenu):
    """The actions menu.
    
    This gets its menu items from portal_actions.
    """

class IDisplaySubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the display menu.
    """
    
    def disabled(self):
        """Find out if the menu is visible but disabled."""

class IDisplayMenu(IBrowserMenu):
    """The display menu.
    
    This gets its menu items from an IBrowserDefault (see CMFDynamicViewFTI).
    """
    
class IFactoriesSubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the factories menu.
    """
    
class IFactoriesMenu(IBrowserMenu):
    """The factories menu.
    
    This gets its menu items from portal_types' list of addable types in 
    the context.
    """

class IWorkflowSubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the workflow menu.
    """

class IWorkflowMenu(IBrowserMenu):
    """The workflow menu.
    
    This gets its menu items from the list of possible transitions in 
    portal_workflow.
    """