from setuptools import find_packages, setup

from regex.__init__ import __version__


with open('README.md') as file:
    long_description = file.read()

with open('requirements.txt') as file:
    requirements = file.read().strip().split('\n')


setup(
    name='regex-peterhunt',
    version=__version__,
    author='Peter Hunt',
    author_email='huangtianhao@icloud.com',
    description='An attempt of recreating Regex with Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/peter-hunt/regex',
    setup_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',

)
