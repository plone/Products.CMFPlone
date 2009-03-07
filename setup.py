from setuptools import setup, find_packages
import os

version = '1.1.9'

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
      url='http://pypi.python.org/pypi/plone.app.layout',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.app.viewletmanager',
        'plone.memoize',
        'plone.portlets',
      ],
      )
