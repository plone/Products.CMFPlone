# This is from Products.PloneHotfix20160830.
from urllib.parse import urlparse
from z3c.form import widget


# Attribute name to allow prefilling a widget with a value from a GET request.
# Usually all forms are only for POST, and we disallow filling it with GET
# data.  This works the way around too: allow prefilling from a POST request
# when the form only handles GET.  But that is unlikely.
ALLOW_PREFILL = 'allow_prefill_from_GET_request'


def _wrap_update(update):
    def _wrapped(self):
        # If we are ignoring the request on the form, we should also ignore it
        # on the widget.  This means that when on the first widget we conclude
        # that the form should be ignored, we quickly ignore it on all widgets,
        # without needing to check the referer and method again and again.
        # When we do not ignore the request, we do still run these checks for
        # all widgets.  But it seems an international sport to override the
        # update or updateWidgets method of the base z3c form, which makes it
        # hard to fix all occurrences by one check on the form.
        if not self.ignoreRequest and getattr(self.form, 'ignoreRequest', False):
            self.ignoreRequest = True
        # If we are not already ignoring the request, check the request method.
        if (not self.ignoreRequest
                and hasattr(self.form, 'method')
                and hasattr(self.request, 'REQUEST_METHOD')):
            if self.request.REQUEST_METHOD.lower() != self.form.method.lower():
                # This is an unexpected request method.
                # For special cases we allow a form to bail out.
                if not getattr(self.form, ALLOW_PREFILL, False):
                    self.ignoreRequest = True
                    self.form.ignoreRequest = True
        # If we are not already ignoring the request, check the referer.
        if not self.ignoreRequest and hasattr(self.request, 'environ'):
            env = self.request.environ
            referrer = env.get('HTTP_REFERER', env.get('HTTP_REFERRER'))
            if referrer:
                req_url_parsed = urlparse(self.request.URL)
                referrer_parsed = urlparse(referrer)
                if req_url_parsed.netloc != referrer_parsed.netloc:
                    # We do not trust data from outside referrers.
                    self.ignoreRequest = True
                    self.form.ignoreRequest = True
        return update(self)
    return _wrapped


widget.Widget.update = _wrap_update(widget.Widget.update)
