from setuptools import find_packages
from setuptools import setup


version = '3.2.2.dev0'

long_description = \
    open("README.rst").read() + "\n" + open("CHANGES.rst").read()

setup(name='plone.app.layout',
      version=version,
      description="Layout mechanisms for Plone",
      long_description=long_description,
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 5.1",
          "Framework :: Plone :: 5.2",
          "Framework :: Zope2",
          "Framework :: Zope :: 4",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
      ],
      keywords='plone layout viewlet',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='https://pypi.org/project/plone.app.layout',
      license='GPL version 2',
      packages=find_packages(),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Acquisition',
          'DateTime',
          'plone.app.content',
          'plone.app.portlets',
          'plone.app.viewletmanager >=1.2',
          'plone.batching >1.0.999',
          'plone.i18n',
          'plone.memoize',
          'plone.portlets',
          'plone.registry',
          'Products.CMFCore',
          'Products.CMFDynamicViewFTI',
          'Products.CMFEditions >=1.2.2',
          'Products.CMFPlone >=5.0b3.dev0',
          'setuptools',
          'six',
          'zope.component',
          'zope.deferredimport',
          'zope.deprecation',
          'zope.dottedname',
          'zope.i18n',
          'zope.interface',
          'zope.publisher',
          'zope.schema',
          'zope.viewlet',
          'Zope2',
      ],
      extras_require=dict(
          test=[
              'plone.app.contenttypes',
              'plone.app.intid',
              'plone.app.relationfield',
              'plone.app.testing',
              'plone.dexterity',
              'plone.locking',
              'plone.testing',
              'z3c.relationfield',
              'zope.annotation',
          ]
      ),
      )
