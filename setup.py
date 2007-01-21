from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='plone.app.controlpanel',
      version=version,
      description="Formlib-based controlpanels for Plone.",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone controlpanel formlib',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.app.controlpanel',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
