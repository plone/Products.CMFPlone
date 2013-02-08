import os
import unittest
import robotsuite
from plone.testing import layered

from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_ACCEPTANCE_TESTING


def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, 'robot')
    robot_tests = [
        os.path.join('robot', doc) for doc in os.listdir(robot_dir)
        if doc.endswith('.txt') and doc.startswith('robot_')
    ]
    for test in robot_tests:
        suite.addTests([
            layered(
                robotsuite.RobotTestSuite(test),
                layer=PRODUCTS_CMFPLONE_ACCEPTANCE_TESTING
            ),
        ])
    return suite
