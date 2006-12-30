from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from Products.Archetypes.mimetype_utils import getAllowableContentTypes
from Products.Archetypes.mimetype_utils import getAllowedContentTypes

from Products.CMFCore.utils import getToolByName


class AllowableContentTypesVocabulary(object):
    """Vocabulary factory for allowable content types.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        items = [ (t, t) for t in getAllowableContentTypes(context)]
        items.sort()
        return SimpleVocabulary.fromItems(items)

AllowableContentTypesVocabularyFactory = AllowableContentTypesVocabulary()


class AllowedContentTypesVocabulary(object):
    """Vocabulary factory for allowed content types.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        items = [ (t, t) for t in getAllowedContentTypes(context)]
        items.sort()
        return SimpleVocabulary.fromItems(items)

AllowedContentTypesVocabularyFactory = AllowedContentTypesVocabulary()


class PortalTypesVocabulary(object):
    """Vocabulary factory for available portal types.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        ttool = getToolByName(context, 'portal_types')
        items = [ (ttool[t].Title(), t)
                  for t in ttool.listContentTypes() ]
        items.sort()
        return SimpleVocabulary.fromItems(items)

PortalTypesVocabularyFactory = PortalTypesVocabulary()


class WorkflowStatesVocabulary(object):
    """Vocabulary factory for workflow states.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        wtool = getToolByName(context, 'portal_workflow')
        items = wtool.listWFStatesByTitle(filter_similar=True)
        items.sort()
        return SimpleVocabulary.fromItems(items)

WorkflowStatesVocabularyFactory = WorkflowStatesVocabulary()
