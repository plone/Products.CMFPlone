from interface import Interface, Attribute

class IOrderedContainer(Interface):
    """ An interface for folders that support ordering
    of items """

    def moveObject(id, position):
        """ Move an object to a given position """

    def getObjectPosition(id):
        """ Get the position (order) of an object given its id """

    def moveObjectUp(id, steps=1, RESPONSE=None):
        """ Move the object up 'steps' number of steps """

    def moveObjectDown(id, steps=1, RESPONSE=None):
        """ Move the object down 'steps' number of steps """

    def moveObjectTop(id, RESPONSE=None):
        """ Move the object the first position """

    def moveObjectBottom(id, RESPONSE=None):
        """ Move the object to the last position """

