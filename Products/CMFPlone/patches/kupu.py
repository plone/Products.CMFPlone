#####################
# Newly created sites

from AccessControl.Permission import _registeredPermissions
from AccessControl.Permission import ApplicationDefaultPermissions
from AccessControl.Permission import pname
from Products.kupu.plone import permissions


mangled = pname(permissions.ManageLibraries)
if hasattr(ApplicationDefaultPermissions, mangled):
    delattr(ApplicationDefaultPermissions, mangled)


if permissions.ManageLibraries in _registeredPermissions:
    del _registeredPermissions[permissions.ManageLibraries]


permissions.setDefaultRoles(
    permissions.ManageLibraries,
    ('Manager', 'Site Administrator',)
    )
