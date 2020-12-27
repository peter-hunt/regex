from setuptools import find_packages, setup

from regex.__init__ import __version__

with open('README.md') as file:
    long_description = file.read()

setup(
    name='regex-peter-hunt',
    version=__version__,
    author='Peter Hunt',
    author_email='huangtianhao@icloud.com',
    description='An attempt of recreating Regex with Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/peter-hunt/regex',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
)
