from interface import Interface, Attribute

class IControlPanel(Interface):
    """ Interface for the ControlPanel """

    def registerConfiglet( id
                 , name
                 , action
                 , condition=''
                 , permission=''
                 , category='Plone'
                 , visible=1
                 , appId=None
                 , imageUrl=None
                 , REQUEST=None
                 ):
        """ Registration of a Configlet """

    def unregisterConfiglet(id):
        """ unregister Configlet """

    def unregisterApplication(appId):
        """ unregister Application with all configlets """

    def getGroupIds():
        """ list of the group ids """

    def getGroups():
        """ list of groups as dicts with id and title """
        
    def enumConfiglets(group=None,appId=None):
        """ lists the Configlets of a group, returns them as dicts by
            calling .getAction() on each of them """

