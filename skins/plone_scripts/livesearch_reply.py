## Script (Python) "livescript_reply"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=q,limit=10
##title=Determine whether to show an id in an edit form

from Products.CMFCore.utils import getToolByName
ploneUtils = getToolByName(context, 'plone_utils')

# SIMPLE CONFIGURATION
USE_ICON = True
USE_RANKING = False
MAX_DESC = 55

# generate a result set for the query
catalog = context.portal_catalog

friendly_types = ploneUtils.getUserFriendlyTypes()

def quotestring(s):
    return '"%s"' % s

def quote_bad_chars(s):
    bad_chars = ["(", ")"]
    for char in bad_chars:
        s = s.replace(char, quotestring(char))
    return s

# for now we just do a full search to prove a point, this is not the
# way to do this in the future, we'd use a in-memory probability based
# result set.
# convert queries to zctextindex
r=q.split(' ')
r = " AND ".join(r)
r = quote_bad_chars(r)+'*'
searchterms = r.replace(' ','+')

results = catalog(SearchableText=r, portal_type=friendly_types)

RESPONSE = context.REQUEST.RESPONSE
RESPONSE.setHeader('Content-Type', 'text/xml')

if not results:
    print '''<fieldset class="livesearchContainer">'''
    print '''<legend id="livesearchLegend">LiveSearch &darr;</legend>'''
    print '<div id="LSNothingFound">No matching results found.</div>'
    print '''</fieldset>'''

else:
    print '''<fieldset class="livesearchContainer">'''
    print '''<legend id="livesearchLegend">LiveSearch &darr;</legend>'''
    print '''<ul class="LSTable">'''
    for result in results[:limit]:
        print '''<li class="LSRow">''',
        print '''<img src="/%s"/>''' % result.getIcon,
        print '''<a href="%s">%s</a>''' % (result.getURL(), result.Title)
        print '''<span class="discreet">[%s%%]</span>''' % result.data_record_normalized_score_
        print '''<div class="discreet" style="margin-left: 2.5em;">%s</div>''' % (result.Description)
        print '''</li>'''
    if len(results)>limit:
        # add a more... row
        print '''<li class="LSRow">'''
        print '<a href="%s" style="font-weight:normal">More...</a>' % ('search?SearchableText=' + searchterms)
        print '''</li>'''
    print '''</ul>'''
    print '''</fieldset>'''

return printed

