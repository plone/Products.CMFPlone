from interface import Interface, Attribute

class IControlPanel(Interface):
    """ Interface for the ControlPanel """

    def registerConfiglet(id, appId, label, templateUrl, image, group, url):
        """ Registration of a Configlet """

    def unregisterConfiglet(configletId):
        """ unregister Configlet """

    def unregisterApplication(appId):
        """ unregister Application with all configlets """

    def getGroupIds():
        """ list of the group ids """

    def getGroups():
        """ list of groups as dicts with id and title """
        
    def enumConfiglets(group=None,appId=None):
        """ lists the Configlets of a group """

