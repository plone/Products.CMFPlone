## Script (Python) "plonifyActions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template_id, actions=None, default_tab='view'
##

from urllib import unquote
here_url = context.absolute_url()
site_properties=context.portal_properties.site_properties

if actions is None:
    actions=context.portal_actions.listFilteredActionsFor()

actionlist=[]
if same_type(actions, {}):
    if context.getTypeInfo().getId() in \
        site_properties.getProperty('use_folder_tabs', ['Folder', 'Large Plone Folder', 'Plone Site']):
        actionlist=actions['folder']+actions['object']
    else:
        actionlist=actions['object']

plone_actions=[]
use_default=1

request_url = context.REQUEST['ACTUAL_URL']
request_url_path = request_url[len(here_url):]
if request_url_path.startswith('/'):
    request_url_path = request_url_path[1:]

for action in actionlist:
    item={'title':'',
          'id':'',
          'url':'',
          'selected':''}

    item['title']=action['title']
    item['id']=actionid=action['id']

    aurl=action['url'].strip()
    if not (aurl.startswith('http') or aurl.startswith('javascript')):
        item['url']='%s/%s'%(here_url,aurl)
    else:
        item['url']=aurl

    action_method=item['url'].split('/')[-1]

    # Action method may be a method alias: Attempt to resolve to a template.
    try:
        action_method=context.getTypeInfo().queryMethodID(action_method,
                                                          default = action_method)
    except AttributeError:
        # Don't raise if we don't have a CMF 1.5 FTI
        pass

    # we unquote since view names sometimes get escaped
    request_action = unquote( request_url_path )
    try:
        request_action=context.getTypeInfo().queryMethodID(request_action,
                                                           default = request_action)
    except AttributeError:
        # Don't raise if we don't have a CMF 1.5 FTI
        pass
    
    if action_method:
        if action_method==template_id or action_method == request_action:
            item['selected']=1
            use_default=0

    plone_actions.append(item)

if use_default:
    for action in plone_actions:
        if action['id']==default_tab:
            action['selected']=1
            break

first = ['folderContents']
plone_actions.sort(lambda a, b: a['id'] in first and -1 or
                                b['id'] in first and 1 or 0)

return plone_actions
