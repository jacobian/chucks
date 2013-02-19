import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "chucks",
    version = "1.0",
    description = "Chucks - a framework for developing technical training material.",
    long_description = read('README.rst'),
    url = 'http://github.com/jacobian/chucks',
    license = 'BSD',
    author = 'Jacob Kaplan-Moss',
    author_email = 'jacob@jacobian.org',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = [
        "Jinja2 >= 2.6, <2.7",
        "Unipath >= 0.2, <0.3",
        "docopt >= 0.4.0, <0.5",
        "Sphinx >= 1.1, <1.2",
        "envoy == 0.0.2",
        "lxml >= 2.3, <2.4",
        "pyPdf == 1.13",
        "lxml >= 2.3, <2.4",
        "pyyaml >= 3.1, <3.2",
    ],

    entry_points = {
        'console_scripts': ['chucks = chucks.cli:main']
    }
)
