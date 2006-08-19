from StringIO import StringIO

def importVarious(context):
    """
    Import various settings.

    Provisional handler that does initialization that is not yet taken
    care of by other handlers.
    """
    site = context.getSite()
    out = StringIO()
    
    logger = context.getLogger("plone.app.portlets")
    logger.info(out.getvalue())