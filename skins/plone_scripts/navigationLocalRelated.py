## Script (Python) "navigationLocalRelated"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=encapsulates the related box
##

local = []
remote = []
subjects=None

if obj is None:
    obj=context

abs_url = obj.absolute_url()
portal_url = context.portal_url.getPortalObject().absolute_url()

if hasattr(obj.aq_explicit, 'Subject'):
    subjects=obj.Subject()

if subjects:
    for o in context.portal_catalog( Subject = subjects
                                   , review_state = 'published'
                                   , sort_on = 'portal_type'
                                   , sort_order = 'reverse'  ):
        url=o.getURL()
        rurl = o.getRemoteUrl
        title=''
        if o.Title:
            title=o.Title
        else:
            title=o.getId #getId() is indexed as the getId property
            
        lnk = {'title':title
               ,'url':url
               ,'icon':o.getIcon}
        if rurl and not rurl.startswith(portal_url): #we need UIDs
            local.append(lnk)
        else:
            remote.append(lnk)

return {'local':local, 'remote':remote}
