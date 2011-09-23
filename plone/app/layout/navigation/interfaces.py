from zope.interface import Interface, Attribute

class INavigationRoot(Interface):
    """A marker interface for signaling the navigation root.
    """

class IDefaultPage(Interface):
    """Interface for a view that can determine if its context is the
    default page or not.
    """

    def isDefaultPage(obj):
        """Finds out if the given obj is the default page for the
        adapted object.
        """

    def getDefaultPage():
        """Returns the id of the default page for the adapted object.
        """

class INavigationQueryBuilder(Interface):
    """An object which returns a catalog query when called, used to
    construct a navigation tree.
    """

    def __call__():
        """Returns a mapping describing a catalog query used to build a
           navigation structure.
        """

class INavtreeStrategy(Interface):
    """An object that is used by buildFolderTree() to determine how to
    construct a navigation tree.
    """

    rootPath = Attribute("The path to the root of the navtree (None means use portal root)")

    showAllParents = Attribute("Whether or not to show all parents of the current context always")

    def nodeFilter(node):
        """Return True or False to determine whether to include the given node
        in the tree. Nodes are dicts with at least one key - 'item', the
        catalog brain of the object the node represents.
        """

    def subtreeFilter(node):
        """Return True or False to determine whether to expand the given
        (folderish) node
        """

    def decoratorFactory(node):
        """Inject any additional keys in the node that are needed and return
        the new node.
        """

    def showChildrenOf(object):
        """Given an object (usually the root of the site), determine whether
        children should be shown or not. Even if this returns True, if
        showAllParents is True, the path to the current item may be shown.
        """
