from Interface import Interface

class ICustomizationPolicy(Interface):
    """
    A Customization Policy is responsible for setting up a raw
    Plone instance according to the instruction provided for the
    Policy.  The Policy must register via
    Products.CMFPlone.Portal.addPolicy
    """

    def customize(portal):
        """
        the customize method takes the portal object and massages
        it.  the only thing that really needs to be understood is that
        the Policy itself is not persisted.

        Most likely a
        CustomizationPolicy would be derived from the
        DefaultCustomizationPolicy, you would call its customize()
        method and then continue on customization the portal.
        """

    def getPloneGenerator():
        """ returns a PloneGenerator, can be overloaded,
            this method is called _before_ the portal is instanciated
        """
