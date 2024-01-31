#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup

#find packages
import setuptools
def find_packages():
    packages = []
    for package in setuptools.find_packages():
        if package.startswith('upsonic_on_prem'):
            packages.append(package)
    return packages


with open('requirements.txt') as fp:
    install_requires = fp.read()
setup(
    name="upsonic_on_prem",
    version="0.5.10",
    description="""Magic Cloud Layer""",
    long_description="".join(open("README.md", encoding="utf-8").readlines()),
    long_description_content_type="text/markdown",
    url="https://github.com/Upsonic/On-Prem",
    author="Upsonic",
    author_email="onur.atakan.ulusoy@upsonic.co",
    license="MIT",
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        "console_scripts": ["upsonic_on_prem=upsonic_on_prem.main:cli"],
    },    
    python_requires=">= 3",
    zip_safe=False,
)


