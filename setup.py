#!/usr/bin/env python
from setuptools import setup, find_packages
VERSION = "1.0.0"


setup_info = dict(
    # Metadata
    name="pyliff",
    version=VERSION,
    author="Freddie Wang",
    author_email="wangyung@gmail.com",
    url="https://github.com/wangyung/pyliff",
    download_url="",
    description="pyliff is a CLI tool to let developers to setup LIFF (LINE Frontend Framework) easily",
    license="BSD",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Build Tools",
    ],

    keywords="liff",

    # Package info
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={'': ['liff']},
    include_package_data=True,
    install_requires=[
        "requests",
    ],

    # Add _ prefix to the names of temporary build dirs
    options={
        "build": {"build_base": "_build"},
    },
    zip_safe=True,
)

setup(**setup_info)
