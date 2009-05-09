from setuptools import setup, find_packages
import os

version = '1.2'

setup(name='plone.app.controlpanel',
      version=version,
      description="Formlib-based controlpanels for Plone.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone controlpanel formlib',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.controlpanel',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.app.form',
        'plone.app.workflow',
        'plone.fieldsets',
        'plone.memoize',
        'plone.protect',
        'plone.locking',
      ],
      )

