from zope.component import adapts
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase


class AccountPanelSchemaAdapter(SchemaAdapterBase):

    adapts(ISiteRoot)

    def __init__(self, context):

        mt = getToolByName(context, 'portal_membership')
        
        if mt.isAnonymousUser():
            raise "Can't modify properties of anonymous user"
        else:
            self.context = mt.getAuthenticatedMember()

