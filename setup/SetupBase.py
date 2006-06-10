from Products.CMFPlone.utils import log_deprecated

class SetupWidget:
    # if single is set to one, then we will
    # show radio buttons rather than check boxes
    single = 0

    def __init__(self, portal):
        self.portal = portal
        log_deprecated("SetupWidget is deprecated and will be removed in Plone"
                       " 3.0. Site creation is based on GenericSetup now.")


    #####################################################
    # To be overridden

    def addItems(self, items):
        """ Adds the items into our Plone database
        Items - a list of things that means something
        to this widget, for example the languages widget
        takes the abbreviations of the pot files
        """
        raise NotImplementedError

    def delItems(self, items):
        """ Dels the items out of our Plone database
        Items - a list of things that means something
        to this widget, for example the languages widget
        takes the abbreviations of the pot files
        """
        raise NotImplementedError

    def active(self):
        """ Returns 1 if this setup widget can be run,
        if the user doesn't have the correct products, for
        example, then a string of the reason why is returned
        """

        # by default this is 1
        return 1

    def setup(self):
        """ Anything that has to be done for this setup widget
        to work, this could be adding in new objects or such. """

        # by default this is working out of the box, ha!
        pass

    def installed(self):
        """ Returns a list of the installed items, so that user
        knows what is currently installed. These items are what
        we would pass to the addItems and delItems methods """
        raise NotImplementedError
