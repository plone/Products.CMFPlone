from setuptools import setup, find_packages

version = '2.0a4'

setup(name='plone.app.layout',
      version=version,
      description="Layout mechanisms for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        ],
      keywords='plone layout viewlet',
      author='Martin Aspeli',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.layout',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.app.viewletmanager>=1.2',
        'plone.memoize',
        'plone.portlets',
        'Products.CMFEditions>=1.2.2',
        'Plone>=4.0dev',
      ],
      )
