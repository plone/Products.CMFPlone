## Script (Python) "personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=portrait=None
##title=Personalization Handler.

from Products.CMFPlone import transaction_note
portrait_id='MyPortrait'

member=context.portal_membership.getAuthenticatedMember()
member.setProperties(context.REQUEST)
    
context.portal_skins.updateSkinCookie()
    
#if a portait file was uploaded put it in the /Members/XXXX/.personal/MyPortrait
if portrait and portrait.filename:
    personal=context.getPlonePersonalFolder()
    if not personal:
        home=context.portal_membership.getHomeFolder()
        home.manage_addProduct['CMFCore'].manage_addContent(type='Portal Folder', id='.personal')
        personal=getattr(home, '.personal')
    if not hasattr(personal, portrait_id):
        personal.invokeFactory(type_name='Image', id=portrait_id)
    portrait_obj=getattr(personal, portrait_id, None)
    portrait_obj.edit(file=portrait)

tmsg=member.getUserName()+' personalized their settings.'
transaction_note(tmsg)

return ('success',  context, {})
