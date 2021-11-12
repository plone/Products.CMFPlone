# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.schema import Bool


class INextPreviousProvider(Interface):
    """A folderish component capable of describing the next and previous
    item relative to a particular id.
    """

    enabled = Bool(title=u"True if next/previous behaviour is enabled")

    def getNextItem(obj):
        """Returns information about next item in the container relative to
        the given object.

        This is a dict with the following keys:

            - id, the id of the object
            - url, the url of the object
            - title, the title of the object
            - description, a description of the object
            - portal_type, the object's portal type
        """

    def getPreviousItem(obj):
        """Returns the previous item in the container relative to the given
        object
        """
