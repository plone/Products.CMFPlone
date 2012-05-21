## Script (Python) "getPortalTypeList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=

from Products.CMFCore.utils import getToolByName

pt_tool = getToolByName(context, 'portal_types')
plone_utils = getToolByName(context, 'plone_utils')
normalizeString = plone_utils.normalizeString

type_info = pt_tool.listTypeInfo()

excluded_ids = {
    'TempFolder': None,
    'CMF Document': None,
    'CMF Event': None,
    'CMF File': None,
    'CMF Folder': None,
    'CMF Image': None,
    'CMF Large Plone Folder': None,
    'CMF Link': None,
    'CMF News Item': None,
    'CMF Topic': None,
    'ATCurrentAuthorCriterion': None,
    'ATDateRangeCriterion': None,
    'ATDateCriteria': None,
    'ATListCriterion': None,
    'ATPathCriterion': None,
    'ATRelativePathCriterion': None,
    'ATPortalTypeCriterion': None,
    'ATReferenceCriterion': None,
    'ATBooleanCriterion': None,
    'ATSelectionCriterion': None,
    'ATSimpleIntCriterion': None,
    'ATSimpleStringCriterion': None,
    'ATSortCriterion': None,
}

result = []
for item in type_info:
    item_id = item.getId()
    if item_id not in excluded_ids:
        result.append({
            'id': normalizeString(item_id),
            'icon': item.getIcon(),
        })

result = [(x['id'], x) for x in result]
result.sort()
result = [x[-1] for x in result]

return result
