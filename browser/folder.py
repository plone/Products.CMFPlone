class FolderView:

    def __init__(self, context):
        self.context = context

        self.standalone = 1
        self.contentTypes = self.context.getAllowedTypes()
        self.contentFilter = self.context.contentFilter or self.context.request.contentFilter() or None
        self.b_size = b_size or self.context.request.b_size or 100
        self.view_title = view_title or request.view_title or ''
        self.contentsMethod = test(here.portal_type==Topic here.queryCatalog here.getFolderContents)
        self.batch = batch or contentsMethod(contentFilterbatch=True b_size=b_size)
        self.full_view = full_view or request.full_view or True
