from setuptools import setup, find_packages

version = '2.5.4'

long_description = \
    open("README.rst").read() + "\n" + open("CHANGES.rst").read()

setup(name='plone.app.layout',
      version=version,
      description="Layout mechanisms for Plone",
      long_description=long_description,
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
      ],
      keywords='plone layout viewlet',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.layout',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Acquisition',
          'DateTime',
          'plone.app.content',
          'plone.app.portlets',
          'plone.app.viewletmanager >=1.2',
          'plone.i18n',
          'plone.memoize',
          'plone.portlets',
          'plone.registry',
          'Products.CMFCore',
          'Products.CMFDynamicViewFTI',
          'Products.CMFEditions >=1.2.2',
          'Products.CMFPlone >=4.3',  # XXX: should be 5.0
          'setuptools',
          'zope.component',
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
