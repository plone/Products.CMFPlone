from plone.protect import protect, CheckAuthenticator


def patch(callable):
    """ apply csrf-protection decorator to the given callable """
    return protect(callable, CheckAuthenticator)


def applyPatches():
    """ apply csrf-protection decorator to all relevant methods """

    from Products.CMFPlone.MigrationTool import MigrationTool
    MigrationTool.upgrade = patch(MigrationTool.upgrade)

    from Products.CMFPlone.PloneTool import PloneTool as PT
    PT.changeOwnershipOf = patch(PT.changeOwnershipOf)
    PT.acquireLocalRoles = patch(PT.acquireLocalRoles)
    PT.deleteObjectsByPaths = patch(PT.deleteObjectsByPaths)
    PT.transitionObjectsByPaths = patch(PT.transitionObjectsByPaths)
    PT.renameObjectsByPaths = patch(PT.renameObjectsByPaths)

    from plone.session.plugins.session import SessionPlugin as SP
    SP.manage_clearSecrets = patch(SP.manage_clearSecrets)
    SP.manage_createNewSecret = patch(SP.manage_createNewSecret)

    from Products.CMFCore.RegistrationTool import RegistrationTool
    RegistrationTool.addMember = patch(RegistrationTool.addMember)

    from Products.CMFCore.MembershipTool import MembershipTool as MT
    from Products.CMFPlone.MembershipTool import MembershipTool as PMT
    MT.setPassword = patch(MT.setPassword)
    PMT.setPassword = patch(PMT.setPassword)
    MT.setRoleMapping = patch(MT.setRoleMapping)
    MT.deleteMemberArea = patch(MT.deleteMemberArea)
    MT.setLocalRoles = patch(MT.setLocalRoles)
    MT.deleteLocalRoles = patch(MT.deleteLocalRoles)
    MT.deleteMembers = patch(MT.deleteMembers)

    from Products.CMFCore.WorkflowTool import WorkflowTool as WT
    WT.manage_changeWorkflows = patch(WT.manage_changeWorkflows)
    WT.setDefaultChain = patch(WT.setDefaultChain)
    WT.setChainForPortalTypes = patch(WT.setChainForPortalTypes)
    WT.updateRoleMappings = patch(WT.updateRoleMappings)

    from Products.CMFDefault.RegistrationTool import RegistrationTool
    RegistrationTool.editMember = patch(RegistrationTool.editMember)

    from Products.DCWorkflow.States import StateDefinition
    StateDefinition.setPermissions = patch(StateDefinition.setPermissions)
    StateDefinition.setPermission = patch(StateDefinition.setPermission)
    StateDefinition.setGroups = patch(StateDefinition.setGroups)

    from Products.DCWorkflow.WorkflowUIMixin import WorkflowUIMixin as UIM
    UIM.setProperties = patch(UIM.setProperties)
    UIM.addManagedPermission = patch(UIM.addManagedPermission)
    UIM.delManagedPermissions = patch(UIM.delManagedPermissions)
    UIM.addGroup = patch(UIM.addGroup)
    UIM.delGroups = patch(UIM.delGroups)
    UIM.setRoles = patch(UIM.setRoles)

    from AccessControl.User import BasicUserFolder as BUF
    BUF.userFolderAddUser = patch(BUF.userFolderAddUser)
    BUF.userFolderEditUser = patch(BUF.userFolderEditUser)
    BUF.userFolderDelUsers = patch(BUF.userFolderDelUsers)
    BUF.manage_setUserFolderProperties = patch(
        BUF.manage_setUserFolderProperties)
    BUF._addUser = patch(BUF._addUser)
    BUF._changeUser = patch(BUF._changeUser)
    BUF._delUsers = patch(BUF._delUsers)
    BUF.manage_users = patch(BUF.manage_users)

    from Products.PlonePAS import pas
    from Products.PluggableAuthService.PluggableAuthService import \
         PluggableAuthService as PAS
    PAS.userFolderAddUser = patch(PAS.userFolderAddUser)
    PAS.userFolderEditUser = patch(PAS.userFolderEditUser)
    PAS.userFolderDelUsers = patch(PAS.userFolderDelUsers)

    from AccessControl.Owned import Owned
    Owned.manage_takeOwnership = patch(Owned.manage_takeOwnership)
    Owned.manage_changeOwnershipType = patch(Owned.manage_changeOwnershipType)

    from AccessControl.PermissionMapping import RoleManager as PMRM
    PMRM.manage_setPermissionMapping = patch(PMRM.manage_setPermissionMapping)

    from AccessControl.Role import RoleManager as RMRM
    RMRM.manage_role = patch(RMRM.manage_role)
    RMRM.manage_acquiredPermissions = patch(RMRM.manage_acquiredPermissions)
    RMRM.manage_permission = patch(RMRM.manage_permission)
    RMRM.manage_changePermissions = patch(RMRM.manage_changePermissions)
    RMRM.manage_addLocalRoles = patch(RMRM.manage_addLocalRoles)
    RMRM.manage_setLocalRoles = patch(RMRM.manage_setLocalRoles)
    RMRM.manage_delLocalRoles = patch(RMRM.manage_delLocalRoles)
    RMRM._addRole = patch(RMRM._addRole)
    RMRM._delRoles = patch(RMRM._delRoles)

    from OFS.DTMLMethod import DTMLMethod
    DTMLMethod.manage_proxy = patch(DTMLMethod.manage_proxy)

    from Products.PythonScripts.PythonScript import PythonScript
    PythonScript.manage_proxy = patch(PythonScript.manage_proxy)

