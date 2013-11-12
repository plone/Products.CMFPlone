from AccessControl import Owned, getSecurityManager
from Acquisition import aq_base, aq_get, aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneFolder import PloneFolder as TempFolderBase
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from Products.CMFPlone.utils import _createObjectByType
from zope.interface import implements


class FauxArchetypeTool(object):
    """A faux archetypes tool which prevents content from being indexed."""

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, tool):
        self.tool = tool

    def getCatalogsByType(self, type_name):
        return []

    def __getitem__(self, id):
        return getattr(self.tool, id)


# #############################################################################
# A class used for generating the temporary folder that will
# hold temporary objects.  We need a separate class so that
# we can add all types to types_tool's allowed_content_types
# for the class without having side effects in the rest of
# the portal.
class TempFolder(TempFolderBase):

    portal_type = meta_type = 'TempFolder'
    isPrincipiaFolderish = 0

    implements(IHideFromBreadcrumbs)

    # override getPhysicalPath so that temporary objects return a full path
    # that includes the acquisition parent of portal_factory (otherwise we get
    # portal_root/portal_factory/... no matter where the object will reside)

    def getPhysicalPath(self):
        '''Returns a path (an immutable sequence of strings)
        that can be used to access this object again
        later, for example in a copy/paste operation.  getPhysicalRoot()
        and getPhysicalPath() are designed to operate together.
        '''
        portal_factory = aq_parent(aq_inner(self))
        path = (aq_parent(portal_factory).getPhysicalPath() +
                (portal_factory.getId(), self.getId(), ))
        return path

    # override / delegate local roles methods
    def __ac_local_roles__(self):
        """__ac_local_roles__ needs to be handled carefully.
        Zope's and GRUF's User.getRolesInContext both walk up the
        acquisition hierarchy using aq_parent(aq_inner(obj)) when
        they gather local roles, and this process will result in
        their walking from TempFolder to portal_factory to the portal root."""
        object = aq_parent(aq_parent(self))
        local_roles = {}
        while 1:
            # Get local roles for this user
            lr = getattr(object, '__ac_local_roles__', None)
            if lr:
                if callable(lr):
                    lr = lr()
                lr = lr or {}
                for k, v in lr.items():
                    if not k in local_roles:
                        local_roles[k] = []
                    for role in v:
                        if not role in local_roles[k]:
                            local_roles[k].append(role)

            # Check if local role has to be acquired (PLIP 16)
            if getattr(object, '__ac_local_roles_block__', None):
                # Ok, we have to stop there, as lr. blocking is enabled
                break

            # Prepare next iteration
            inner = getattr(object, 'aq_inner', object)
            parent = getattr(inner, 'aq_parent', None)
            if parent is not None:
                object = parent
                continue
            if hasattr(object, 'im_self'):
                object = object.im_self
                object = getattr(object, 'aq_inner', object)
                continue
            break
        return local_roles

    def has_local_roles(self):
        return len(self.__ac_local_roles__())

    def get_local_roles_for_userid(self, userid):
        return tuple(self.__ac_local_roles__().get(userid, []))

    def get_valid_userids(self):
        return aq_parent(aq_parent(self)).get_valid_userids()

    def valid_roles(self):
        return aq_parent(aq_parent(self)).valid_roles()

    def validate_roles(self, roles):
        return aq_parent(aq_parent(self)).validate_roles(roles)

    def userdefined_roles(self):
        return aq_parent(aq_parent(self)).userdefined_roles()

    # delegate Owned methods
    def owner_info(self):
        return aq_parent(aq_parent(self)).owner_info()

    def getOwner(self, info=0, aq_get=aq_get,
                 UnownableOwner=Owned.UnownableOwner,
                 getSecurityManager=getSecurityManager,
                 ):
        return (aq_parent(aq_parent(self))
                .getOwner(info, aq_get, UnownableOwner, getSecurityManager))

    def userCanTakeOwnership(self):
        return aq_parent(aq_parent(self)).userCanTakeOwnership()

    # delegate allowedContentTypes
    def allowedContentTypes(self):
        return aq_parent(aq_parent(self)).allowedContentTypes()

    def __getitem__(self, id):
        # Zope's inner acquisition chain for objects returned by __getitem__
        # will be portal -> portal_factory -> temporary_folder -> object
        #
        # What we really want is for the inner acquisition chain to be
        # intended_parent_folder
        #     `-> portal_factory
        #             `-> temporary_folder
        #                     `-> object
        # So we need to rewrap...
        portal_factory = aq_parent(aq_inner(self))
        intended_parent = aq_parent(portal_factory)

        # If the intended parent has an object with the given id, just do a
        # passthrough
        if hasattr(intended_parent, id):
            return getattr(intended_parent, id)

        # rewrap portal_factory
        portal_factory = aq_base(portal_factory).__of__(intended_parent)
        # rewrap self
        temp_folder = aq_base(self).__of__(portal_factory)

        if id in self:
            return ((aq_base(self._getOb(id)).__of__(temp_folder))
                    .__of__(intended_parent))
        else:
            type_name = self.getId()
            try:
                # We fake an archetype tool which returns no catalogs for the
                # object to be indexed in to avoid it showing up in the catalog
                # in the first place.
                real_at_tool = getToolByName(self, 'archetype_tool')
                fake_at_tool = FauxArchetypeTool(real_at_tool)
                self.archetype_tool = fake_at_tool
                _createObjectByType(type_name, self, id)
            except ConflictError:
                raise
            except:
                # some errors from invokeFactory (AttributeError, maybe others)
                # get swallowed -- dump the exception to the log to make sure
                # developers can see what's going on
                log_exc(severity=logging.DEBUG)
                raise
            obj = self._getOb(id)

            # keep obj out of the catalog
            obj.unindexObject()

            # additionally keep it out of Archetypes UID and refs catalogs
            if base_hasattr(obj, '_uncatalogUID'):
                obj._uncatalogUID(obj)
            if base_hasattr(obj, '_uncatalogRefs'):
                obj._uncatalogRefs(obj)

            return (aq_base(obj).__of__(temp_folder)).__of__(intended_parent)

    # ignore rename requests since they don't do anything
    def manage_renameObject(self, id, new_id, REQUEST=None):
        pass
