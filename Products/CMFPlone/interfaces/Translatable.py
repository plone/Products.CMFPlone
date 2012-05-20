from zope.deprecation import deprecated
from zope.interface import Interface


class ITranslatable(Interface):
    """
    Interface for translatable content.
    """

    def isTranslation():
        """
        return language if this object is used as multilingual content, 0
        otherwise
        """

    def addTranslation(language, **kwargs):
        """
        Add a new language translation of this content.
        """

    def removeTranslation(language):
        """
        Removes a translation
        """

    def getTranslation(language='language'):
        """
        Return the object corresponding to a translated version or None.
        If called without arguments it returns the translation in the currently
        selected language, or self.
        """

    def getTranslationLanguages():
        """
        Return a list of language codes
        """

    def getTranslations():
        """
        Return a dict of {lang : [object, wf_state]}
        """

    def isCanonical():
        """
        boolean, is this the original, canonical translation of the content.
        """

    def getCanonicalLanguage():
        """
        Return the language code for the canonical translation of this content.
        """

    def getCanonical():
        """
        Return the original, canonical translation of this content.
        """

    def setLanguage(language):
        """
        Sets the language for the current translation - same as DC
        """

    def Language():
        """
        Returns the language of this translation - same as DC
        """

deprecated("ITranslatable",
        "Please use Products.LinguaPlone.interfaces.ITranslatable instead. "
        "This interface will be removed in Plone 5.0")
