from zope.interface import Attribute
from zope.interface import Interface


class IImageScalesAdapter(Interface):
    """
    Return a list of image scales for the given context
    """

    def __init__(context, request):
        """Adapts context and the request."""

    def __call__():
        """ """


class IImageScalesFieldAdapter(Interface):
    """ """

    def __init__(field, context, request):
        """Adapts field, context and request."""

    def __call__():
        """Returns JSON compatible python data."""
