#!/usr/bin/env python3
# Purpose: install local dependencies and apply local configuration changes
# See:
#    https://docs.python.org/3/distutils/setupscript.html#setup-script
#    https://pypi.python.org/pypi?%3Aaction=list_classifiers
# Usage:
#    prepare source distribution:
#       python3 setup.py sdist
#    initialise local distribution:
#       python3 -m pip install .
#    initialise local distribution (distutils, does not pick up `install_requires`):
#       python3 setup.py install
# https://python-packaging.readthedocs.io/en/latest/minimal.html

import sys
from distutils.core import setup

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 6)
if CURRENT_PYTHON < REQUIRED_PYTHON:
   sys.stderr.write('CURRENT_PYTHON: {} REQUIRED_PYTHON: {}'.format(REQUIRED_PYTHON, CURRENT_PYTHON))
   sys.exit(1)

setup(name='AWS Serverless Wordcount',
      version='0.0.1',
      description='Wordcount facility for PDF exposed as a serverless API',
      license='MIT',
      author='Antony Cartwright',
      author_email='antonyccartwright@gmail.com',
      url='https://polycode.co.uk/',
      download_url='https://github.com/antonycc/aws-serverless-wordcount',
      install_requires=['PyPDF2>=1.26','timeout-decorator>=0.4.0'],
      zip_safe=False,
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Environment :: Other Environment',
          'Framework :: Pytest',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Unix Shell',
          'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Text Processing',
          'Topic :: Utilities'
          ],
     )
