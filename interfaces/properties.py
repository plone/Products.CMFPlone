""" CMFPlone tool interfaces.

$Id: _tools.py 38762 2005-10-05 10:44:00Z yuppie $
"""

from zope.interface import Interface
from zope.interface import Attribute

_marker = object()

#
#   Site Properties tool interface
#
class IPropertiesTool(Interface):

    """ Manage properties of the site as a whole.
    """

    id = Attribute('id',
            """ The tool's ID.

            o BBB:  for use in 'getToolByName';  in the future, prefer
              'zapi.getUtility(IPropertiesTool)'.

            o Must be set to 'portal_properties'.
            """)

    def editProperties(props):
        """ Change portal settings.

        o 'props' is a mapping of values to be updates.

        o Permission:  Manage portal
        """

    def title():
        """ Return the site's title.
        """

    def smtp_server():
        """ Return the configured SMTP server for the site.
        """

class ISimpleItemWithProperties(Interface):
    pass
