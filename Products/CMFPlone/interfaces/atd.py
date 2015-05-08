from zope.interface import Interface


class IATDProxyView(Interface):
    """ Proxy view for the 'After the Deadline" spellchecker
    """

    def checkDocument(self):
        """ Proxy for the AtD service's checkDocument function
            See http://www.afterthedeadline.com/api.slp for more info.
        """
