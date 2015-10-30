""" CMFPlone product permissions """
from AccessControl import ModuleSecurityInfo

security = ModuleSecurityInfo('Products.CMFPlone.permissions')

security.declarePublic('AccessContentsInformation')
from Products.CMFCore.permissions import AccessContentsInformation

security.declarePublic('AddPortalContent')
from Products.CMFCore.permissions import AddPortalContent

security.declarePublic('AddPortalFolders')
from Products.CMFCore.permissions import AddPortalFolders

security.declarePublic('AddPortalMember')
from Products.CMFCore.permissions import AddPortalMember

security.declarePublic('DeleteObjects')
from Products.CMFCore.permissions import DeleteObjects

security.declarePublic('FTPAccess')
from Products.CMFCore.permissions import FTPAccess

security.declarePublic('ListFolderContents')
from Products.CMFCore.permissions import ListFolderContents

security.declarePublic('ListPortalMembers')
from Products.CMFCore.permissions import ListPortalMembers

security.declarePublic('ListUndoableChanges')
from Products.CMFCore.permissions import ListUndoableChanges

security.declarePublic('ManagePortal')
from Products.CMFCore.permissions import ManagePortal

security.declarePublic('ManageProperties')
from Products.CMFCore.permissions import ManageProperties

security.declarePublic('ManageUsers')
from Products.CMFCore.permissions import ManageUsers

security.declarePublic('ModifyPortalContent')
from Products.CMFCore.permissions import ModifyPortalContent

security.declarePublic('ReplyToItem')
from Products.CMFCore.permissions import ReplyToItem

security.declarePublic('RequestReview')
from Products.CMFCore.permissions import RequestReview

security.declarePublic('ReviewPortalContent')
from Products.CMFCore.permissions import ReviewPortalContent

security.declarePublic('SetOwnPassword')
from Products.CMFCore.permissions import SetOwnPassword

security.declarePublic('SetOwnProperties')
from Products.CMFCore.permissions import SetOwnProperties

security.declarePublic('UndoChanges')
from Products.CMFCore.permissions import UndoChanges

security.declarePublic('View')
from Products.CMFCore.permissions import View

security.declarePublic('ViewManagementScreens')
from Products.CMFCore.permissions import ViewManagementScreens
