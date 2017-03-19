from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = "pcbmode",
    packages = find_packages(exclude=['tests', 'docs']),
    use_scm_version=True,
    setup_requires=['setuptools_scm'],

    install_requires = ['lxml', 'pyparsing'],

    package_data = {
        'pcbmode': ['stackups/*.json',
                    'styles/*/*.json',
                    'fonts/*.svg',
                    'pcbmode_config.json'],
    },

    # metadata for upload to PyPI
    author = "Saar Drimer",
    author_email = "saardrimer@gmail.com",
    description = "A printed circuit board design tool with a twist",
    long_description = long_description,
    license = "MIT",
    keywords = "pcb svg eda pcbmode",
    url = "https://github.com/boldport/pcbmode",

    entry_points={
        'console_scripts': ['pcbmode = pcbmode.pcbmode:main']
    },
    zip_safe = True
)

