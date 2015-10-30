from zope.interface import Interface


# Language-support
class ILanguage(Interface):

    def get_language(self):
        """ return the contents language """

    def set_language(self):
        """ return the contents language """
