"""
This file will hold fixes between versions which will be moved to
migrations after release.
"""

def fix_portal_properties_id(self):
    """
    Fix portal_properties copy support. The objects where
    being created with an empty id, which resulted in
    manage_copyObject copying the container instead of the
    object.
    """
    pp = self.portal_properties
    for i in pp.objectIds():
        psheet = getattr(pp, i)
        psheet.id = str(i)
    return "Fixed portal_properties property sheets id."
        
