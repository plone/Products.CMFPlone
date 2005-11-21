from Interface import Interface

#Portions of this class was copy/pasted from the OFS.IOrderSupport from
#Zope2.7.  This class is licensed under the ZPL 2.0 as stated here:
#http://www.zope.org/Resources/ZPL
#Zope Public License (ZPL) Version 2.0
#This software is Copyright (c) Zope Corporation (tm) and Contributors. All rights reserved.

class IOrderedContainer(Interface):
    """ Ordered Container interface.

    This interface provides a common mechanism for maintaining ordered
    collections.
    """

    def moveObjectsByDelta(ids, delta, subset_ids=None):
        """ Move specified sub-objects by delta.

        If delta is higher than the possible maximum, objects will be moved to
        the bottom. If delta is lower than the possible minimum, objects will
        be moved to the top.

        If subset_ids is not None, delta will be interpreted relative to the
        subset specified by a sequence of ids. The position of objects that
        are not part of this subset will not be changed.

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
