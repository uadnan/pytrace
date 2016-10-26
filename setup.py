from setuptools import setup, find_packages
from codecs import open
from os import path

import pytrace

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pytrace',
    version=pytrace.__version__,
    description='Python Execution Trace Collector',
    long_description=long_description,
    url='https://github.com/uadnan/pytrace',
    license='MIT',

    # Author details
    author='Adnan Umer',
    author_email='u.adnan@outlook.com',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Education :: System',
        'License :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='visualizer visualization',

    packages=find_packages(exclude=['tests']),
    install_requires=[
        'enum34',
        'six>=1.10.0'
    ],
    extras_require={
        'dev': [
            'nose>=1.3.7',
            'unittest2>=1.1.0'
        ],
    }
)
