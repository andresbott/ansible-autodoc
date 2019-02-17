#!/usr/bin/python3

import os
import sys
import glob

sys.path.insert(0, os.path.abspath('src'))
from ansibleautodoc import __version__


try:
    from setuptools import setup, find_packages,Command
except ImportError:
    print("ansible-autodoc needs setuptools in order to build. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)

# https://github.com/dave-shawley/setupext-janitor
try:
    from setupext import janitor
    CleanCommand = janitor.CleanCommand
except ImportError:
    print("Module 'setupext' not available, clean command will not clean everything")
    CleanCommand = None

cmd_classes = {}
if CleanCommand is not None:
    cmd_classes['clean'] = CleanCommand



with open("README.md", "r") as fh:
    long_description = fh.read()

def get_template_files():
    file_list = []
    base_dir = "src/templates"
    for file in glob.glob(base_dir+'/**/*.*', recursive=True):
        file_list.append(file)
    return file_list

template_files = get_template_files()

setup(
    name="ansible-autodoc",
    version=__version__,
    author="Andres Bott",
    author_email="contact@andresbott.com",
    description='Generate documentation from annotated playbooks and roles using templates',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AndresBott/ansible-autodoc",
    package_dir={'': 'src'},
    packages=find_packages("src"),
    include_package_data=True,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Topic :: Software Development',
        'Topic :: Software Development :: Documentation',
    ],
    install_requires=[
        'jinja2',
        'pyyaml',
    ],
    setup_requires=['setupext'],
    scripts=[
        'src/bin/ansible-autodoc',
    ],
    cmdclass=cmd_classes,

)

