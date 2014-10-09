from zope.interface import Interface, Attribute


class IScriptsView(Interface):

    def scripts():
        """ Returns a list of dicts with information for scripts rendering. """


class IStylesView(Interface):

    def styles():
        """ Returns a list of dicts with information for style rendering. """


