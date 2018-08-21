from setuptools import setup, find_packages

with open('requirements.txt') as fp:
    install_requires = fp.read()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='aiohttp_boilerplate',
    version='',
    install_requires=install_requires,
    packages=find_packages(),
    license='',
    author='webdeveloppro',
    author_email='',
    description=long_description
)
