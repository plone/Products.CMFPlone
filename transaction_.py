#
# Zope 2.8-style transaction module for Zope <= 2.7.
#

# $Id: zopetransaction.py 8925 2005-06-03 00:43:31Z shh42 $

def get():
    return get_transaction()

def begin():
    get_transaction().begin()

def commit(sub=False):
    get_transaction().commit(sub)

def abort(sub=False):
    get_transaction().abort(sub)

