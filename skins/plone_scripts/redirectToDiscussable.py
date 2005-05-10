## Script (Python) "redirectToDiscussable"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Redirect from a discussionItem to it's absolute parent (discussable object)
##

if context.portal_type == 'Discussion Item':
  redirect_target = context.plone_utils.getDiscussionThread(context)[0]
  view = redirect_target.getTypeInfo().getActionById('view')
  anchor = context.id
  
  context.REQUEST['RESPONSE'].redirect( redirect_target.absolute_url()
         + '/%s#%s' % (view, anchor) )