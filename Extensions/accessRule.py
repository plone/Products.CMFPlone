# This Access Rule is used by installers so that when you install
# Plone straight out of the box, port 80 will show up as the Plone site.
#
# If you are running mulitple sites then you probably won't want to use
# this instead I'd recommend using VirtualHostMonster and a Proxy server
# that can do rewriting such as Apache or Squid (see the Zope or Plone books
# for more information). To remove this access the root ZMI and 
# select 'Set Access Rule' to disable the access rule
# (yes that is a little odd).
#
# The installer sets up a default Plone site for you, called Plone (this
# is assigned to siteObj variable). To all you to get to the root this access
# rule will accept an environment variable called HTTP_MANAGE to point to the
# value of the manager port. This value is normally 8080 and is set by the 
# zope.conf file.
#
# The Plone installer adds this in as an External Method point to accessRule.
# If a request comes in and its not the HTTP_MANAGE port then its going to 
# append Plone into the path.
# 
# This will work with FTP, WebDAV and all other protocols.

import os
HTTP_MANAGE = os.environ.get('HTTP_MANAGE', '')
siteObj = 'Plone'

def accessRule(self, *args):
    if self.REQUEST.get('SERVER_PORT', '') != HTTP_MANAGE and self.REQUEST['URL'].find(siteObj) < 0:
        self.REQUEST['TraversalRequestNameStack'].append(siteObj)
        self.REQUEST.set('SiteRootPATH', '/')
