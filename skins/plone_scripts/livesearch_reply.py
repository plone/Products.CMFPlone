## Script (Python) "livescript_reply"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=q,limit=10
##title=Determine whether to show an id in an edit form

# SIMPLE CONFIGURATION
USE_ICON = True
USE_RANKING = False
MAX_DESC = 55

# generate a result set for the query
catalog = context.portal_catalog

# for now we just do a full search to prove a point, this is not the
# way to do this in the future, we'd use a in-memory probability based
# result set.

# convert queries to zctextindex
q=q.split(' ')
r=[]
searchterms='+'.join(q)
for w in q:
    r.append("%s*" % w)
    
r = " and ".join(r)
results = catalog(SearchableText=r)

# filter out certain types
filter=['Subscription', 'Favorite', 'ATDateCriteria', 'ATListCriterion', 'ATPortalTypeCriterion', 'ATSimpleIntCriterion', 'ATSimpleStringCriterion', 
        'ATSortCriterion', 'Alias', 'ICESubscription']

results = [r for r in results if not r.portal_type in filter]

RESPONSE = context.REQUEST.RESPONSE
RESPONSE.setHeader('Content-Type', 'text/xml')

#baseurl = context.portal_url()

if not results:
    print '<table id="LSTable" class="livesearchContainer" style="width:16em">'
    print '<tr><td style="white-space:nowrap;text-align:center"><br/>No results<br/><br /></td></tr></table>'

else:

    print '''<table id="LSTable" class="livesearchContainer">'''
    for result in results[:limit]:
        print "<tr>"
        print '<td class="LSRow">'

        #print '''<img src="/%s"/>''' % result.getIcon,
        print '''<a href="%s"><img src="/%s"/>&nbsp;%s&nbsp;<span style="font-weight:normal">[%s%%]</span></a>''' % (result.getURL()+'/view?searchterm=' + searchterms, result.getIcon, result.Title or result.id, result.data_record_normalized_score_)

            
        if len(result.Description)>MAX_DESC:
            Desc = result.Description[:MAX_DESC] + '...'
        else:
            Desc = result.Description

        print '''<div class="LSDescr">%s</div>''' % (Desc)
        print '''</td></tr>'''
        
    if len(results)>limit:
        # add a more... row
        print "<tr>"
        print '<td class="LSRow">'
        print '<a href="%s" style="font-weight:normal">More...</a>' % ('search?SearchableText=' + searchterms)
        print '</td></tr>'
        
    print '''</table>'''


    #print '''<fieldset class="livesearchContainer">'''
    #print '''<ul class="LSRes">'''
    #for result in results[:limit]:
        #print '''<li class="LSRow">''',

        #if USE_ICON:
            #print '''<img src="/%s"/>''' % result.getIcon,

        #print '''<a href="%s">%s</a>''' % (result.getURL(), result.Title)

        #if USE_RANKING:
            #print '''<span class="discreet">[%s%%]</span>''' % result.data_record_normalized_score_

        #print '''<div class="discreet" style="margin-left: 2.5em;">%s</div>''' % (result.Description)
        #print '''</li>'''
    #print '''</ul>'''
    #print '''</fieldset>'''

return printed

