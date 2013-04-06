from zope.interface import Interface


ACQUIRE = -1  # acquire locallyAllowedTypes from parent (default)
DISABLED = 0  # use default behavior of PortalFolder,
              # which uses the FTI information
ENABLED = 1  # allow types from locallyAllowedTypes only


class IConstrainTypes(Interface):
    """
    Interface for folderish content types supporting restricting addable types
    on a per-instance basis.
    """

    def getConstrainTypesMode():
        """
        Find out if add-restrictions are enabled. Returns 0 if they are
        disabled (the type's default FTI-set allowable types is in effect),
        1 if they are enabled (only a selected subset if allowed types will be
        available), and -1 if the allowed types should be acquired from the
        parent. Note that in this case, if the parent portal type is not the
        same as the portal type of this object, fall back on the default (same
        as 0)
        """

    def getLocallyAllowedTypes():
        """
        Get the list of FTI ids for the types which should be allowed to be
        added in this container.
        """

    def getImmediatelyAddableTypes():
        """
        Return a subset of the FTI ids from getLocallyAllowedTypes() which
        should be made most easily available.
        """

    def getDefaultAddableTypes():
        """
        Return a list of FTIs which correspond to the list of FTIs available
        when the constraint mode = 0 (that is, the types addable without any
        setLocallyAllowedTypes trickery involved)
        """

    def allowedContentTypes():
        """
        Return the list of currently permitted FTIs.
        """


class ISelectableConstrainTypes(IConstrainTypes):
    """
    Extension to the IConstrainTypes interface for content types which allow
    the user to set the allowable content types and immediately available
    types.
    """

    def setConstrainTypesMode(mode):
        """
        Set how addable types is controlled in this class. If mode is 0, use
        the type's default FTI-set allowable types). If mode is 1, use only
        those types explicitly enabled using setLocallyAllowedTypes(). If
        mode is -1, acquire the allowable types from the parent. If the parent
        portal type is not the same as this object's type, fall back on the
        behaviour obtained if mode == 0.
        """

    def setLocallyAllowedTypes(types):
        """
        Set a list of type ids which should be allowed. This must be a
        subset of the type's FTI-set allowable types. This list only comes
        into effect when the restrictions mode is 1 (enabled).
        """

    def setImmediatelyAddableTypes(types):
        """
        Set the list of type ids which should be immediately/most easily
        addable. This list must be a subset of any types set in
        setLocallyAllowedTypes.
        """

    def canSetConstrainTypes():
        """
        Return True if the current user is permitted to constrain addable
        types in this folderish object.
        """
