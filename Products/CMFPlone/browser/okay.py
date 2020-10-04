from Products.Five.browser import BrowserView


class OK(BrowserView):
    """Returns OK.

    Useful for automated checks, for example httpok, to see if the site
    is still available.  For this you don't want to query a possibly
    expensive page.  And you don't want to query anything that may be
    stored in an intermediate caching server.

    Calling /ZopeTime can work too.  But if you use
    experimental.publishtraverse, this will either give you a NotFound,
    or log a warning each time it is called, due to lacking
    permissions.  And this may happen in core Plone in the future too.
    """

    def __call__(self):
        # Make really sure this response is not cached.  This is what
        # plone/app/caching/operations/utils.py does in the doNotCache
        # function.
        set_header = self.request.response.setHeader
        set_header('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
        set_header('Cache-Control', 'max-age=0, must-revalidate, private')
        # Return a short and simple message.
        return 'OK'
