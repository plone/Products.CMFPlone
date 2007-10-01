# script to strip the group_ prefix from all local roles 

from Acquisition import aq_base 

def do(self): 
    """Do it!""" 
    print '---' 
    removePrefix(self) 
    # Reindex security settings recursively
    self.reindexObjectSecurity()
    print '---' 
    return 'Done!' 
     
def removePrefix(folder): 
    """Recursive function""" 
    for id in folder.objectIds(): 
        obj = folder._getOb(id) 
        local_roles = getattr(aq_base(obj), '__ac_local_roles__', None) 

        if local_roles is not None: 
            needs_updating = [(r, local_roles[r]) for r in local_roles \
                                                   if r.startswith('group_')] 
            old = local_roles 
            for name, roles in needs_updating: 
                new_name = name[6:] 
                del local_roles[name] 
                local_roles[new_name] = roles 

            if needs_updating: 
                print 'Updating: ', obj.getPhysicalPath() 
                print 'Old: ', old 
                obj.__ac_local_roles__ = local_roles 
                print 'New: ', local_roles 

        if obj.objectIds(): 
            removePrefix(obj)
