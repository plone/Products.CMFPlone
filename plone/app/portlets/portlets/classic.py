from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base


class IClassicPortlet(IPortletDataProvider):
    """A portlet which can render a classic Plone portlet macro
    """

    template = schema.ASCIILine(title=_(u'Template'),
                            description=_(u'The template containing the portlet.'),
                            required=True)

    macro = schema.ASCIILine(title=_(u'Macro'),
                         description=_(u"The macro containing the portlet."),
                         default='portlet',
                         required=True)

class Assignment(base.Assignment):
    implements(IClassicPortlet)

    def __init__(self, template='', macro=''):
        self.template = template
        self.macro = macro

    @property
    def title(self):
        return self.template

class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.request = request
        self.data = data

    render = ViewPageTemplateFile('classic.pt')

    def use_macro(self):
        return bool(self.data.macro)

    def path_expression(self):
        expr = 'context/%s' % self.data.template
        if self.use_macro():
            expr += '/macros/%s' % self.data.macro
        return expr

class AddForm(base.AddForm):
    form_fields = form.Fields(IClassicPortlet)
    label = _(u"Add Classic Portlet")
    description = _(u"A classic portlet allows you to use legacy portlet templates.")

    def create(self, data):
        return Assignment(template=data.get('template', ''),
                          macro=data.get('macro', ''))

class EditForm(base.EditForm):
    form_fields = form.Fields(IClassicPortlet)
    label = _(u"Edit Classic Portlet")
    description = _(u"A classic portlet allows you to use legacy portlet templates.")
