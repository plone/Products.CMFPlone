import re
from zope.i18n import translate

from Acquisition import aq_base
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from plone.memoize.instance import memoize
from plone.app.layout.viewlets.common import ViewletBase

HEADING_RE = re.compile('<(h[12])([^>]*)>', re.IGNORECASE)


class PresentationView(BrowserView):

    # BBB; can be removed in Plone 5
    @property
    def template(self):
        return self.index

    def __call__(self):
        return self.template()

    @memoize
    def body(self):
        return self.context.CookedBody()

    def enabled(self):
        getPresentation = getattr(aq_base(self.context), "getPresentation", None)
        if getPresentation is None or getPresentation() == False:
            return False

        body = self.body()
        return bool(HEADING_RE.search(body))

    def content(self):
        # ugly, ugly, ugly code, that basically changes the way the slide is put
        # together this should be a HTML parser or XSLT or even JS

        body = self.body()
        m = HEADING_RE.search(body)
        tag = m.group(1)

        num = int(tag[1])
        if num > 1:
            new = "%s1" % (tag[0])
            body = HEADING_RE.sub(r'<%s\2>' % new, body)
            body = body.replace("</%s>" % tag, "</%s>" % new)
            tag = new

        body = re.sub(r'(<%s[^>]*>)' % tag, r'</div><div class="slide">\n\1', body)
        if body.startswith('</div>'):
            body = body[6:]
        body += '</div>'
        return body

    @memoize
    def creator(self):
        return self.context.Creator()

    def author(self):
        membership = getToolByName(self.context, "portal_membership")
        return membership.getMemberInfo(self.creator())

    def authorname(self):
        author = self.author()
        return author and author['fullname'] or self.creator()


class PresentationViewlet(ViewletBase):

    def update(self):
        getPresentation = getattr(self.context.aq_base, "getPresentation", None)
        self.presentation_enabled = False
        if getPresentation is not None:
            try:
                self.presentation_enabled = getPresentation()
            except KeyError:
                # schema not updated yet
                self.presentation_enabled = False

    def render(self):
        if self.presentation_enabled:
            url = "%s/presentation_view" % self.context.absolute_url()
            msg = _(u'Also available in presentation mode\u2026')
            msg = translate(msg, domain='plone', context=self.request)
            return u'<p id="link-presentation"><a href="%s" rel="nofollow" class="link-presentation">%s</a></p>' % (url, msg)
        return u''
