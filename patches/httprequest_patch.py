from ZPublisher.HTTPRequest import HTTPRequest
from exceptions import AssertionError

def stripFormData(self):
    """\
    Monkey-patched by Plone to add this method.
    Strip form data from self, before traversing (otherwise
    they'll be used again in the template we traverse to).

    Compare ZPublisher.HTTPRequest.clone().
    """
    for key in self.form.keys():
        del self.other[key]
    self.form.clear()
    if 'QUERY_STRING' in self.environ:
        del self.environ['QUERY_STRING']

HTTPRequest.stripFormData = stripFormData

