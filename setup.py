#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
from setuptools import setup, find_packages

try:
    from numpy.distutils.core import Extension
    import numpy
except:
    from pip._internal import main as pip
    pip(['install', 'numpy'])

try:
    from Cython.Distutils import build_ext
except:
    from pip._internal import main as pip
    pip(['install', 'cython'])

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
        'h5py',
        'pandas',
        'numpy',
        'scipy',
        'xarray',
        'netcdf4',
        ]

setup_requirements = [ ]

test_requirements = [ ]

extensions = [
        Extension(
            "LayerObjects",              # Extension name
            sources=[f'c_extensions/LayerObjs.pyx',], # Cython source filename
            language="c++",              # Creates C++ source
            extra_compile_args=['-O3'],
            include_dirs = [numpy.get_include(),f'{os.getcwd()}/include'],
            ),
        ]

setup(
    author="Kevin Smalley",
    author_email='ksmalley@tamu.edu',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="This package contains a set of packages and command line plugins that can identify indidual cloud objects along CloudSat's orbit and their associated properties (i.e. cloud type, size, precipitating)",
    entry_points={
        'console_scripts': [
            'cloudSat_object_creator=cloudsat_object_manipulation.cldObj_creation:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='cloudsat_object_manipulation',
    name='cloudsat_object_manipulation',
    ext_modules = extensions,
    packages=find_packages(include=['cloudsat_object_manipulation']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/kms2213/cloudsat_object_manipulation',
    version='0.1.0',
    zip_safe=False,
    cmdclass = {'build_ext': build_ext}
)
