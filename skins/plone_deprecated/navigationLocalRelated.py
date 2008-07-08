## Script (Python) "navigationLocalRelated"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=encapsulates the related box
##

context.plone_log("The navigationLocalRelated script is deprecated and will be "
                  "removed in Plone 4.0.")

local = []
remote = []
subjects=None
isURLInPortal = context.portal_url.isURLInPortal

if obj is None:
    obj=context

abs_url = obj.absolute_url()
portal_url = context.portal_url.getPortalObject().absolute_url()
pretty_title_or_id = context.plone_utils.pretty_title_or_id

if hasattr(obj.aq_explicit, 'Subject'):
    subjects=obj.Subject()

if subjects:
    for o in context.portal_catalog( Subject = subjects
                                   , sort_on = 'portal_type'
                                   , sort_order = 'reverse'  ):
        url=o.getURL()
        if url == abs_url: continue # s/b if o is obj but fails
        rurl = o.getRemoteUrl # getRemoteUrl is indexed as getRemoteUrl
        title=pretty_title_or_id(o)

        lnk = {'title' : title,
               'url'  : url,
               'rurl' : rurl,
               'icon' : o.getIcon,
              }
        if rurl and not isURLInPortal(rurl): #we need UIDs
            remote.append(lnk)
        else:
            local.append(lnk)

return {'local':local, 'remote':remote}
