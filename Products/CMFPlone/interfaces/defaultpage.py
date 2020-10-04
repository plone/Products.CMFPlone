from zope.interface import Interface


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
