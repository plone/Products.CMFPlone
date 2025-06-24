from urllib.parse import urlparse
from z3c.form import widget

# Allow prefilling a widget from a GET request
ALLOW_PREFILL = "allow_prefill_from_GET_request"

def _wrap_update(update):
    def _wrapped(self):
        form = getattr(self, "form", None)

        # Respect ignoreRequest from the form if set
        if not self.ignoreRequest and getattr(form, "ignoreRequest", False):
            self.ignoreRequest = True

        # Check if request method matches form's expected method
        if (
            not self.ignoreRequest
            and hasattr(form, "method")
            and hasattr(self.request, "REQUEST_METHOD")
        ):
            if self.request.REQUEST_METHOD.lower() != form.method.lower():
                if not getattr(form, ALLOW_PREFILL, False):
                    self.ignoreRequest = True
                    if form:
                        form.ignoreRequest = True

        # Check referrer to avoid cross-site prefill
        if not self.ignoreRequest and hasattr(self.request, "environ"):
            env = self.request.environ
            referrer = env.get("HTTP_REFERER", env.get("HTTP_REFERRER"))
            if referrer:
                req_url_parsed = urlparse(self.request.URL)
                referrer_parsed = urlparse(referrer)
                if req_url_parsed.netloc != referrer_parsed.netloc:
                    self.ignoreRequest = True
                    if form:
                        form.ignoreRequest = True

        return update(self)

    return _wrapped

# Patch the widget
widget.Widget.update = _wrap_update(widget.Widget.update)
