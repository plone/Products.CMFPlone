## Script (Python) "plonifyActions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template_id, actions=None
##title=
##
here_url = context.absolute_url()
site_properties=context.portal_properties.site_properties

if actions is None:
    actions=context.portal_actions.listFilteredActionsFor()

actionlist=[]
if same_type(actions, {}):
    if context.getTypeInfo().getId() in site_properties.use_folder_tabs:
        actionlist=actions['folder']+actions['object']+actions.get('object_tabs',[])
    else:
        actionlist=actions['object']+actions.get('object_tabs',[])
   
plone_actions=[]
for action in actionlist:
    item={'name':'',
          'id':'',
          'url':'',
          'selected':''}

    item['name']=action['name']
    item['id']=actionid=action['id']

    aurl=action['url'].strip()
    if not aurl.startswith('http'):
        item['url']='%s/%s'%(here_url,aurl)
    else:
        item['url']=aurl

    if item['url'].split('/')[-1]==template_id:
        item['selected']=1

    plone_actions.append(item)

return plone_actions 


