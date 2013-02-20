import os

from plone.app.testing.interfaces import PLONE_SITE_ID


PORT = os.environ.get('ZSERVER_PORT', 55001)
PORT = os.environ.get('PLONE_TESTING_PORT', PORT)
ZSERVER_PORT = PORT
SELENIUM_IMPLICIT_WAIT = os.environ.get('SELENIUM_IMPLICIT_WAIT', '1s')

ZOPE_HOST = os.environ.get('ZOPE_HOST', "localhost")
ZOPE_URL = os.environ.get('ZOPE_URL', "http://%s:%s" % (ZOPE_HOST, PORT))
PLONE_SITE_ID = os.environ.get('PLONE_SITE_ID', PLONE_SITE_ID)
PLONE_URL = os.environ.get('PLONE_URL', "%s/%s" % (ZOPE_URL, PLONE_SITE_ID))
BROWSER = os.environ.get('BROWSER', "Firefox")
REMOTE_URL = os.environ.get('REMOTE_URL', "")
DESIRED_CAPABILITIES = os.environ.get('DESIRED_CAPABILITIES', "")

TEST_FOLDER = os.environ.get('TEST_FOLDER', "%s/test-folder" % PLONE_URL)
