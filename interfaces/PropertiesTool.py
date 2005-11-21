from Interface import Interface, Attribute

class IPropertiesTool(Interface):

    id = Attribute('id', 'Must be set to "portal_properties"')

    def editProperties(props):
        """ Change portal settings.

        Permission -- ManagePortal
        """

    def smtp_server():
        """ Get local SMTP server.

        Returns -- String
        """

