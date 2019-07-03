# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='Stack Oversight',
    version='0.1.0',
    description='Python library for detecting code duplication with Stack Overflow',
    long_description=readme,
    author='Andrew Walker, Jonathan Simmons, Asher Snavely, Michael Coffey',
    author_email='ires@baylor.edu',
    url='https://ires.ecs.baylor.edu/2019',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

