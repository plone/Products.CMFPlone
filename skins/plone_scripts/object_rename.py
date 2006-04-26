## Python Script "object_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Show the rename form for an object
##

from Products.CMFPlone.utils import transaction_note
from Products.CMFCore.utils import getToolByName
from OFS.CopySupport import CopyError
from AccessControl import Unauthorized
from Products.PythonScripts.standard import url_quote_plus

REQUEST = context.REQUEST

mtool = getToolByName(context, 'portal_membership')
if not mtool.checkPermission('Copy or Move', context):
    raise Unauthorized, context.translate("Permission denied to rename ${title}.",
                                          {'title': context.title_or_id()})

pathName = url_quote_plus('paths:list')
safePath = context.absolute_url_path()
orig_template = REQUEST['HTTP_REFERER'].split('?')[0]
url = 'folder_rename_form?orig_template=%s&%s=%s' % (orig_template,
                                                     pathName, 
                                                     safePath)

REQUEST.RESPONSE.redirect(url)
