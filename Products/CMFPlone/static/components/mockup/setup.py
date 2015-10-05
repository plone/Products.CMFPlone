from setuptools import setup, find_packages
import json

package_json = json.load(open('package.json'))
version = package_json['version']

setup(
    name='mockup',
    version=version,
    description="A collection of client side patterns for faster and easier "
                "web development",
    long_description=open("README.rst").read(),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone mockup',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://github.com/plone/mockup',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points='''
        [z3c.autoinclude.plugin]
        target = mockup
    ''',
)
