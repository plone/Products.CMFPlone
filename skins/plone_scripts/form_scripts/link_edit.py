## Script (Python) "link_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=remote_url, id='', title=None, description=None, subject=None
##title=Edit a link
##

context.edit(remote_url=remote_url)
context.plone_utils.contentEdit( context
                               , id=id
                               , description=description)
return 'success'