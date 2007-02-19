Sitemap testing
===============

First some initial setup code:

    >>> self.loginAsManager()

Obtain the sitemap
------------------

    >>> self.browser.open('http://nohost/plone/sitemap.xml.gz')
    >>> self.browser.url
    'http://nohost/plone/sitemap.xml.gz'
    
    
Get the contents and decode them
    >>> data = self.browser.contents
    >>> from gzip import GzipFile
    >>> from StringIO import StringIO
    >>> sio = StringIO(data)
    >>> fp = GzipFile(fileobj=sio)
    >>> xml = fp.read()
    >>> fp.close()
    
Not sure how to test the XML now as it also contains dates but for now
we will just search for some URLs and tags.

    >>> xml.find('<loc>http://nohost/plone/Members/root</loc>')!=-1
    True
    >>> xml.find('<loc>http://nohost/plone/front-page</loc>')!=-1
    True
    