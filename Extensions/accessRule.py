import os
HTTP_MANAGE = os.environ.get('HTTP_MANAGE', '')
siteObj = 'Plone'

# This access rule adds Plone in..

def accessRule(self, *args):
    if self.REQUEST.get('SERVER_PORT', '') != HTTP_MANAGE and self.REQUEST['URL'].find(siteObj) < 0:
        self.REQUEST['TraversalRequestNameStack'].append(siteObj)
	self.REQUEST.set('SiteRootPATH', '/')



