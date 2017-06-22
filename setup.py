#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import synonym

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pyquery',
    'requests',
    'crayons'
    # TODO: put package requirements here
]

setup_requirements = [
    # TODO(gavinzbq): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='synonym',
    version=synonym.__version__,
    description="synonym: Instant synonym answers via command line.",
    long_description=readme + '\n\n' + history,
    author="Shanyun Gao",
    author_email='shanyun@g.clemson.edu',
    maintainer="Shanyun Gao",
    maintainer_email='shanyun@g.clemson.edu',
    url='https://github.com/gavinzbq/synonym',
    packages=find_packages(include=['synonym']),
    entry_points={
        'console_scripts': [
            'synonym = synonym.synonym:command_line_runner',
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='synonym',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
