#
# Zope 2.8-style transaction module for Zope <= 2.7.
#

# $Id$

# BBB: Zope 2.7

def get():
    return get_transaction()

def begin():
    return get_transaction().begin()

def commit(sub=False):
    return get_transaction().commit(sub)

def abort(sub=False):
    return get_transaction().abort(sub)

def savepoint(optimistic=False):
    # a savepoint is like a subtransaction
    commit(1)
    return DummySavePoint()

class DummyInvalidSavepointRollbackError(Exception):
    pass    

class DummySavePoint:
    """A dummy save point which is always invalid and can't be rolled back
    """
    valid = False
    
    def rollback(self):
        raise DummyInvalidSavepointRollbackError, "I'm only a dummy"

