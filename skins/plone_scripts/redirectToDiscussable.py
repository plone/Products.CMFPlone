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
  state = redirect_target.restrictedTraverse("@@plone_context_state")
  view_url = '%s/%s' % (context.absolute_url(), state.view_template_id())
  anchor = context.id
  
  context.REQUEST['RESPONSE'].redirect(view_url + '#' + anchor)
