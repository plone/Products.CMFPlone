from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='plone.app.layout',
      version=version,
      description="Layout mechanisms for Plone",
      long_description="""\
plone.app.layout contains various visual components for Plone, such as 
viewlets and general views.
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='plone layout viewlet',
      author='Martin Aspeli',
      author_email='optilude@gmx.net',
      url='http://svn.plone.org/svn/plone/plone.app.layout',
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
