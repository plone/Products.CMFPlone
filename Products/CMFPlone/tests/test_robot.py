# -*- coding: utf-8 -*-
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_ROBOT_TESTING_1
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_ROBOT_TESTING_2
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_ROBOT_TESTING_3
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_ROBOT_TESTING_4
from plone.app.testing import ROBOT_TEST_LEVEL
from plone.testing import layered
from itertools import cycle
import os
import unittest
import robotsuite


def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, 'robot')
    robot_tests = [
        os.path.join('robot', doc) for doc in
        os.listdir(robot_dir) if doc.endswith('.robot') and
        doc.startswith('test_')
    ]
    class_cycler = cycle((
        PRODUCTS_CMFPLONE_ROBOT_TESTING_1,
        PRODUCTS_CMFPLONE_ROBOT_TESTING_2,
        PRODUCTS_CMFPLONE_ROBOT_TESTING_3,
        PRODUCTS_CMFPLONE_ROBOT_TESTING_4,
    ))
    for robot_test in robot_tests:
        robottestsuite = robotsuite.RobotTestSuite(
            robot_test,
            noncritical=['unstable'],
        )
        robottestsuite.level = ROBOT_TEST_LEVEL
        suite.addTests([
            layered(
                robottestsuite,
                layer=next(class_cycler)
            ),
        ])
    return suite
