from interface import Interface

class ITempFolder(Interface):
    """ """
    def getPhysicalPath():
        """ """
    def __getitem__(id):
        """ """

class IFactoryTool(Interface):
    """ """

    def docs():
        """ """
    def getFactoryTypes():
        """ """
    def manage_setPortalFactoryTypes(REQUEST, listOfTypeIds):
        """ """
    def doCreate(obj):
        """ """
    def fixRequest():
        """ """
    def isTemporary(obj):
        """ """
    def __before_publishing_traverse__(other, REQUEST):
        """ """
    def __call__(*args, **kwargs):
        """ """
    def getTempFolder(type_name):
        """ """
    def __bobo_traverse__(REQUEST, name):
        """ """
