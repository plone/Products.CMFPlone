from Acquisition import aq_base, aq_inner, aq_parent
from zope.component import getMultiAdapter
#from zope.component import queryMultiAdapter
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

EXCLUDED = ('default', 'metadata', 'dates', 'ownership', 'settings')

class schemataView(BrowserView):
    
    def __init__(self, context, request):
        super(schemataView, self).__init__(context, request)
        self.membership = getToolByName(context, 'portal_membership')
        self.portal_state = getMultiAdapter((self.context, self.request),
                                                name=u'plone_portal_state')
    
    def getSchemataFields(self, schemata, remove_empty=False):
        context = aq_inner(self.context)
        folder = context.aq_parent
        portal = self.portal_state.portal()
        fields = context.Schema().filterFields(schemata=schemata,
                                               isMetadata=False)
        fields = [ field for field in fields
                   if self.membership.checkPermission(field.read_permission,
                                                                    context)
                   and field.widget.isVisible(context,'view') == 'visible'
                   and field.widget.testCondition(folder, portal, context)
                   ]
        if remove_empty:
            # we keep only fields that have a value to display
            fields = [ field for field in fields
                       if getattr(context, field.accessor)() ]
        return tuple(fields)

    def getDefaultFields(self, remove_empty=False):
        return self.getSchemataFields('default', remove_empty)

    def getCollapsibleSchemata(self, remove_empty=False):
        schematas = aq_inner(self.context).Schemata()
        fieldsets = [ {'name': key,} for key in schematas.keys()
                      if key not in EXCLUDED ]
        for fieldset in fieldsets:
            schemata = fieldset['name']
            fieldset['fields'] = self.getSchemataFields(schemata,
                                                        remove_empty)
        return fieldsets

    __call__ = ZopeTwoPageTemplateFile('templates/schemata-view.pt')

"""
      <tal:defaultfields repeat="field python:context.Schema().filterFields(schemata='default', isMetadata=0)">
        <tal:if_visible define="mode string:view;
                                visState python:field.widget.isVisible(context, mode);
                                visCondition python:field.widget.testCondition(context.aq_inner.aq_parent, portal, context);"
                        condition="python:visState == 'visible' and visCondition">
          <metal:use_field use-macro="context/widgets/field/macros/view" />
        </tal:if_visible>

      </tal:defaultfields>
"""