from setuptools import setup, find_packages

version = '1.0b9'

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
          'five.formlib',
          'plone.protect',
          'plone.app.controlpanel >=2.0b1',
          'plone.app.layout',
          'zope.app.form',
          'zope.component',
          'zope.formlib',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
          'zope.site',
          'Plone >= 4.0a4',
          'Products.CMFCore',
          'Products.CMFDefault',
          'Products.statusmessages',
          'Zope2 >= 2.12.3',
          'ZODB3',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
