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
                                   , sort_on = 'portal_type'
                                   , sort_order = 'reverse'  ):
        url=o.getURL()
        if url == abs_url: continue # s/b if o is obj but fails
        rurl = o.getRemoteUrl # getRemoteUrl is index as getRemoteUrl
        title=''
        if o.Title:
            title=o.Title
        else:
            title=o.getId #getId() is indexed as the getId property

        lnk = {'title' : title,
               'url'  : url,
               'rurl' : rurl,
               'icon' : o.getIcon,
              }
        if rurl and not rurl.startswith(portal_url): #we need UIDs
            remote.append(lnk)
        else:
            local.append(lnk)

return {'local':local, 'remote':remote}
