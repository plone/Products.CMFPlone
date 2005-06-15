#
# Zope 2.8-style transaction module for Zope <= 2.7.
#

# $Id$

def get():
    return get_transaction()

def begin():
    get_transaction().begin()

def commit(sub=False):
    get_transaction().commit(sub)

def abort(sub=False):
    get_transaction().abort(sub)

