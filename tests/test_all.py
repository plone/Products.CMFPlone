import Zope
from unittest import main
from Products.CMFCore.tests.base.utils import build_test_suite

def test_suite():

    return build_test_suite('Products.CMFPlone.tests',[
        'test_join',
        'test_Portal',
        ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
