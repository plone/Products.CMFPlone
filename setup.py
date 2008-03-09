from setuptools import setup, find_packages

version = '1.1.0b1'

setup(name='plone.app.portlets',
      version=version,
      description="Plone integration for the basic plone.portlets package",
      long_description="""\
plone.app.portlets provides a Plone-specific user interface for 
plone.portlets, as well as a standard set of portlets that ship with Plone.
""",
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        ],
      keywords='portlets viewlets plone',
      author='Martin Aspeli',
      author_email='optilude@gmx.net',
      url='http://svn.plone.org/svn/plone/plone.app.portlets',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.portlets >=1.1dev',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
