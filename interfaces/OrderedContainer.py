from interface import Interface, Attribute

##class IOrderedContainer(Interface):
##    """ An interface for folders that support ordering
##    of items """
##
##    def moveObject(id, position):
##        """ Move an object to a given position """
##
##    def getObjectPosition(id):
##        """ Get the position (order) of an object given its id """
##
##    def moveObjectUp(id, steps=1, RESPONSE=None):
##        """ Move the object up 'steps' number of steps """
##
##    def moveObjectDown(id, steps=1, RESPONSE=None):
##        """ Move the object down 'steps' number of steps """
##
##    def moveObjectTop(id, RESPONSE=None):
##        """ Move the object the first position """
##
##    def moveObjectBottom(id, RESPONSE=None):
##        """ Move the object to the last position """

from Interface import Interface


class IOrderedContainer(Interface):
    """ Ordered Container interface.

    This interface provides a common mechanism for maintaining ordered
    collections.
    """

    def moveObjectsByDelta(ids, delta):
        """ Move specified sub-objects by delta.

        If delta is higher than the possible maximum, objects will be moved to
        the bottom. If delta is lower than the possible minimum, objects will
        be moved to the top.

        The order of the objects specified by ids will always be preserved. So
        if you don't want to change their original order, make sure the order
        of ids corresponds to their original order.

        If an object with id doesn't exist an error will be raised.

        Permission -- Manage properties

        Returns -- Number of moved sub-objects
        """

    def moveObjectsUp(ids, delta=1):
        """ Move specified sub-objects up by delta in container.

        If no delta is specified, delta is 1. See moveObjectsByDelta for more
        details.

        Permission -- Manage properties

        Returns -- Number of moved sub-objects
        """

    def moveObjectsDown(ids, delta=1):
        """ Move specified sub-objects down by delta in container.

        If no delta is specified, delta is 1. See moveObjectsByDelta for more
        details.

        Permission -- Manage properties

        Returns -- Number of moved sub-objects
        """

    def moveObjectsToTop(ids):
        """ Move specified sub-objects to top of container.

        See moveObjectsByDelta for more details.

        Permission -- Manage properties

        Returns -- Number of moved sub-objects
        """

    def moveObjectsToBottom(ids):
        """ Move specified sub-objects to bottom of container.

        See moveObjectsByDelta for more details.

        Permission -- Manage properties

        Returns -- Number of moved sub-objects
        """

    def orderObjects(key, reverse=None):
        """ Order sub-objects by key and direction.

        Permission -- Manage properties

        Returns -- Number of moved sub-objects
        """

    def getObjectPosition(id):
        """ Get the position of an object by its id.

        Permission -- Access contents information

        Returns -- Position
        """

    def moveObjectToPosition(id, position):
        """ Moves specified object to absolute position.

        Permission -- Manage properties

        Returns -- Number of moved sub-objects
        """