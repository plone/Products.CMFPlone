from interface import Interface, Attribute
#from Products.CMFCore.interfaces.portal_properties import portal_properties

#class IPropertiesTool(portal_properties):
class IPropertiesTool(Interface):

    id = Attribute('id', 'Must be set to "portal_properties"')

    # TODO Interface doesn't know how to deal with ComputedAttribute :(
    # title = Attribute('title', 'A (read-only) property representing the portal title.')

    def editProperties(props):
        """ Change portal settings.

        Permission -- ManagePortal
        """

    def smtp_server():
        """ Get local SMTP server.

        Returns -- String
        """

