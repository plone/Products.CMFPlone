from setuptools import setup, find_packages
import os

version = '1.2'

setup(name='plone.app.layout',
      version=version,
      description="Layout mechanisms for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        ],
      keywords='plone layout viewlet',
      author='Martin Aspeli',
      author_email='optilude@gmx.net',
      url='http://svn.plone.org/svn/plone/plone.app.layout',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'plone.locking',
            'plone.app.controlpanel',
            'zope.annotation',
            'zope.publisher',
            'zope.testing',
            'Products.PloneTestCase',
        ]
      ),
      install_requires=[
        'setuptools',
        'plone.app.viewletmanager>=1.2',
        'plone.memoize',
        'plone.portlets',
        'zope.component',
        'zope.deprecation',
        'zope.dottedname',
        'zope.i18n',
        'zope.interface',
        'zope.schema',
        'zope.viewlet',
        'zope.app.pagetemplate',
        'Plone',
        'Products.CMFCore',
        'Products.CMFDefault',
        # 'Acquisition',
        # 'DateTime',
        # 'Zope2',
      ],
      )
