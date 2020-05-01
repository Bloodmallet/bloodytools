#!/usr/bin/env python

from setuptools import setup

setup(
    name='bloodytools',
    version='1.0',
    author='Bloodmallet(EU)',
    author_email='bloodmalleteu@gmail.com',
    description='Allows multiple ways of automated data generation via SimulationCraft for World of Warcraft.',
    install_requires=[
        'requests',
        'https://github.com/repos/Bloodmallet/simc_support.git@master#egg=simc_support',
    ],
    license='GNU GENERAL PUBLIC LICENSE',
    packages=[
        'bloodytools',
    ],
    package_data={
        "": ["*.md",],
    },
    python_requires='>3.6',
    url='https://github.com/Bloodmallet/bloodytools',
)
