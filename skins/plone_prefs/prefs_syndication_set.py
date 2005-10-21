## Script (Python) "prefs_syndication_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=updatePeriod=None, updateFrequency=None, updateBase=None, isAllowed=None, max_items=None, REQUEST=None, RESPONSE=None
##title=set syndication prefs
##

from Products.CMFPlone import PloneMessageFactory as _
from Products.PythonScripts.standard import url_quote_plus
REQUEST=context.REQUEST

ps = context.portal_syndication

ps.editProperties( updatePeriod=updatePeriod,
                   updateFrequency=updateFrequency,
                   updateBase=updateBase,
                   isAllowed=isAllowed,
                   max_items=max_items,
                   )

msg = _(u'Syndication properties updated')
RESPONSE.redirect('prefs_syndication_form?portal_status_message=' + url_quote_plus(msg))

return
