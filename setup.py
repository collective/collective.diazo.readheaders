from setuptools import setup, find_packages
import os

version = '0.1'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='collective.diazo.readheaders',
      version=version,
      description="Middleware that allows flexible Diazo theme selection based upon incoming HTTP headers. Extends functionality found in Diazo.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='diazo theme wsgi html xslt',
      author='David Beitey',
      author_email='python@davidjb.com',
      url='https://github.com/collective/collective.diazo.readheaders',
      license='gpl',
      packages=find_packages(),
      namespace_packages=['collective', 'collective.diazo'],
      include_package_data=True,
      zip_safe=False,
      setup_requires=[
          'setuptools-git',
      ],
      install_requires=[
          'setuptools',
          'diazo[wsgi]',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.filter_app_factory]
      main = collective.diazo.readheaders:ExtendedDiazoMiddleware
      """,
      )
