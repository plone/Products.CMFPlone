from Interface import Base

class ICustomizationPolicy(Base):
    """ A Customization Policy is responsible for setting up a raw Plone instance according to the 
        instruction provided for the Policy.  The Policy must register via Products.CMFPlone.Portal.addPolicy
    """
    
    def customize(portal):
        """ the customize method takes the portal object and massages it.  the only thing that really needs
	    to be understood is that the Policy itself is not persisted.  most likely a CustomizationPolicy
	    would be derived from the DefaultCustomizationPolicy, you would call its customize() method and tehn
	    continue on customization the portal
        """
