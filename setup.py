#!/usr/bin/env python

from setuptools import setup


setup(name='bloodytools',
  version='1.0',
  author='Bloodmallet(EU)',
  author_email='kruse.peter.1990@gmail.com',
  description='Allows multiple ways of automated data generation via SimulationCraft for World of Warcraft.',
  url='https://github.com/Bloodmallet/bloodytools',
  packages=['bloodytools'],
  package_data={
    "": ["*.md", ],
  },
  python_requires='>3.5',
  license='GNU GENERAL PUBLIC LICENSE',
)
