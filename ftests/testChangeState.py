#
# Functional test of the Change State action of the folder contents page
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


#os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
#os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

app=ZopeTestCase.app()
ZopeTestCase.utils.setupSiteErrorLog(app)
ZopeTestCase.close(app)

ZopeTestCase.utils.startZServer(2)

from Acquisition import aq_base
from Products.CMFPlone.Portal import default_frontpage

from mechanize import Browser
from urllib import urlencode
from urlparse import urlparse
import re

default_user = PloneTestCase.default_user

_d = {'__ac_name': default_user,
      '__ac_password': 'secret'}


class TestChangeState(ZopeTestCase.Functional, PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        # Manually install Plone default frontpage
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', 'index_html', title='Welcome to Plone', 
                                   text_format='html', text=default_frontpage) 
        # Fire up mech browser
        self.portal_url = self.portal.absolute_url()
        self.folder_url = self.folder.absolute_url()
        self.b = Browser()

    def testChangeState(self):
        self.folder.invokeFactory('Document', 'statetest', title='Welcome to Plone',
                           text_format='html', text=default_frontpage)
        # Goto folder_contents of member area and log in by passing in 
        # the username and password in _d.
        self.b.open(self.folder_url+"/folder_contents", urlencode(_d))
        # Select the folder contents form.  We have a named form here, so form selection is
        # nicer.
        self.b.select_form(name="folderContentsForm")
        #select the checkbox for the document        
        self.b["ids:list"]=["statetest",]
        #click the change state button
        #self.failUnless(self.b.open(self.b.click("content_status_history:method")))
        response=self.b.open(self.b.click("content_status_history:method"))
        
        #the following lines were used to track down a bug in mechanize (0.0.7a) and ClientForm (0.1.15)
        #which uses an attribute "uri" of the base tag instead of the correct "href" attribute.
        #print "browser url = ", self.b.geturl()
        #print "response url = ", response.geturl()
        #print response.info()
        
        #import pullparser, sys
        #p = pullparser.PullParser(response)
        #for token in p.tags("base"):
        #  try:
        #    print "base_uri: ", dict(token.attrs).get("href", "NONE")
        #  except pullparser.NoMoreTokensError:
        #    break
        #print response.read()
        #select the edit_form 
        self.b.select_form("edit_form")
        #print "action =",self.b.action
        #print "links =",self.b.links()
        #fail if the document is not in the list of ids to change state
        self.failUnless("statetest" in self.b.possible_items("ids:list"))
        #select the checkbox for the document        
        self.b["ids:list"]=["statetest",]
        # set workflow action to submit and the other form controls to some random value
        self.b["workflow_action"]=["submit"]
        self.b["effective_date_year"]=["2004"]
        self.b["effective_date_month"]=["02"]
        self.b["effective_date_day"]=["10"]
        self.b["effective_date_hour"]=["12"]
        self.b["effective_date_minute"]=["0"]
        self.b["expiration_date_year"]=["2004"]
        self.b["expiration_date_month"]=["04"]
        self.b["expiration_date_day"]=["20"]
        self.b["expiration_date_hour"]=["20"]
        self.b["expiration_date_minute"]=["0"]
        self.b["comment"]="TEST"
        #print out the form controls
        #for control in self.b.controls:
        #  print control.name,control.value          
        #click the change state button
        self.failUnless(self.b.open(self.b.click("form.button.FolderPublish")))
          
if __name__ == '__main__':
    framework()
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestChangeState))
        return suite
