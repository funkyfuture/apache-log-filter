#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="apache-log-filter",
    version="0.1-alpha1",
    description="A library that filters Apache web server's logs with granular filter-sets.",
    author="Frank Sachsenheim",
    author_email="funkyfuture@riseup.net",
    url="https://www.none.yet",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: Log Analysis"
    ],
    install_requires = [ "apache-log-parser>1.3.0" ],
    packages=find_packages(),
)

