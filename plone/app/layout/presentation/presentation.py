from zope.i18n import translate

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from plone.memoize.view import memoize
from plone.app.layout.viewlets.common import ViewletBase

class PresentationView(BrowserView):
    template = ViewPageTemplateFile('presentation.pt')

    def __call__(self):
        return self.template()

    @memoize
    def body(self):
        return self.context.CookedBody()

    @memoize
    def enabled(self):
        getPresentation = getattr(self.context.aq_base, "getPresentation", None)
        if getPresentation is None or getPresentation() == False:
            return False

        body = self.body()

        # this should be a regex too, but hey this works
        tags = ["h1", "H1", "h2", "H2"]
        tag = None
        for t in tags:
            if body.find("<%s>" % t) > -1:
                tag = t
                break

        if tag is None:
            return False

        return True

    def content(self):
        # ugly, ugly, ugly code, that basically changes the way the slide is put
        # together this should be a HTML parser or XSLT or even JS

        body = self.body()

        # this should be a regex too, but hey this works
        tags = ["h1", "H1", "h2", "H2"]
        tag = None
        for t in tags:
            if body.find("<%s>" % t) > -1:
                tag = t
                break

        num = int(tag[1])
        if num > 1:
            new = "%s1" % (tag[0])
            body = body.replace("<%s>" % tag, "<%s>" % new)
            body = body.replace("</%s>" % tag, "</%s>" % new)
            tag = new

        body = body.split('<%s>' % tag)
        body = ('</div>\n<div class="slide">\n<%s>' % tag).join(body)
        body = body.split('</%s>' % tag)
        body = ('</%s>\n' % tag).join(body)

        return body

    @memoize
    def creator(self):
        return self.context.Creator()

    @memoize
    def author(self):
        membership = getToolByName(self.context, "portal_membership")
        return membership.getMemberInfo(self.creator())

    @memoize
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
