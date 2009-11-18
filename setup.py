from setuptools import setup, find_packages

version = '1.0a1'

setup(name='plone.app.users',
      version=version,
      description="A package for all things users and groups related (specific to plone)",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Zope CMF Plone Users Groups',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.app.users',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'zope.testing',
            'Products.PloneTestCase',
        ],
      ),
      install_requires=[
          'setuptools',
          'plone.fieldsets',
          'plone.memoize',
          'plone.protect',
          'plone.app.controlpanel',
          'plone.app.form',
          'zope.component',
          'zope.formlib',
          'zope.interface',
          'zope.schema',
          'zope.app.form',
          'Products.CMFCore',
          'Products.statusmessages',
          'Zope2',
          'ZODB3',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
