## Script (Python) "TitleOrId"
##parameters=dontCall=0
##title=Return Title or getId
if dontCall:
    title = context.Title
    id = context.id
else:
    title = context.Title()
    id = context.getId()
if title:
    return title
else:
    return id
