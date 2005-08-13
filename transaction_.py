#
# Zope 2.8-style transaction module for Zope <= 2.7.
#

# $Id$

# BBB: Zope 2.7

def get():
    return get_transaction()

def begin():
    get_transaction().begin()

def commit(sub=False):
    get_transaction().commit(sub)

def abort(sub=False):
    get_transaction().abort(sub)

def savepoint(optimistic=False):
    # A savepoint is like a subtransaction
    get_transaction().commit(1)
    return DummySavePoint()

class DummySavePoint:
    """A dummy save point which is always invalid and can't be rolled back
    """
    valid = False

    def rollback(self):
        raise RuntimeError, "I'm only a dummy"
