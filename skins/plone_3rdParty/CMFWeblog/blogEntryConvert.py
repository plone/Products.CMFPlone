import string
catalog = context.portal_catalog
# get all blog entry catalog records
blogRec = catalog(Type='Blog Entry')
for blogEntry in blogRec:
    # get entry database object, parent folder, entry source and metadata
    entryObject = blogEntry.getObject()
    entryId = entryObject.getId()
    entryCreated = entryObject.created()
    entryFormat = entryObject.Format()
    parent = entryObject.aq_parent
    src = entryObject.EditableBody()
    wf_state = context.portal_workflow.getInfoFor(entryObject,'review_state','')
    headers = {}
    for data in entryObject.getMetadataHeaders():
        if not data[0].lower() in  ['title', 'subject', 'description,contributors'
                                    ,'effective_date', 'expiration_date', 'format'
                                    , 'languag', 'rights']: continue
        headers[data[0].lower()] = data[1] or ''
    #delete old object and create a new weblog entry with old values
    print 'deleting Blog Entry %s' % entryId
    parent.manage_delObjects(entryObject.getId())
    print 'creating Weblog Entry %s' % entryId
    parent.invokeFactory('Weblog Entry',entryId)
    weblogObject = parent[entryId]
    weblogObject.setDate(entryCreated)
    weblogObject.edit(entryFormat,src)
    weblogObject.editMetadata(**headers)
    if wf_state == 'published':
       context.portal_workflow.doActionFor(weblogObject, 'publish')
       print 'republishing %s' % entryId
return printed


