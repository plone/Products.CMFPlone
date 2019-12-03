import os
import unittest
import robotsuite
from plone.testing import layered

from Products.CMFPlone.testing import CLASSIC_THEME_ROBOT_TESTING
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_ROBOT_TESTING
from Products.CMFPlone.testing import UNSTYLED_THEME_ROBOT_TESTING


def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, 'robot')
    robot_tests = [
        os.path.join('robot', doc) for doc in os.listdir(robot_dir)
        if doc.endswith('.robot') and doc.startswith('test_')
    ]
    for test in robot_tests:
        if 'unstyled' in test:
            layer = UNSTYLED_THEME_ROBOT_TESTING
        elif 'classic' in test:
            layer = CLASSIC_THEME_ROBOT_TESTING
        else:
            layer = PRODUCTS_CMFPLONE_ROBOT_TESTING
        suite.addTests([
            layered(
                robotsuite.RobotTestSuite(test),
                layer=layer
            ),
        ])
    return suite
