import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='auprico-auth',
    version='0.1',
    packages=['auprico_auth'],
    description='automated processes and intelligent components - auth package',
    long_description=README,
    author='Daniele Bernardini',
    author_email='daniele.bernardini@aismart.co',
    url='https://github.com/dani0805/auprico-auth/',
    license='Apache',
    install_requires=[
        'Django>=2.1', 'auprico-core>=0.1'
    ]
)