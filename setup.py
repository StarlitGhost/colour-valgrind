try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found,"
          "could not convert markdown README to RST")
    read_md = lambda f: open(f, 'r').read()

config = {
    'name': 'colour-valgrind',
    'version': '0.3.5',
    'description': 'Wraps Valgrind to colour the output.',
    'long_description': read_md('README.md'),
    'author': 'Matthew Cox',
    'url': 'http://github.com/MatthewCox/colour-valgrind',
    'author_email': 'matthewcpcox@gmail.com',
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Text Processing :: Filters',
        'Topic :: Utilities',
        ],
    'keywords': 'valgrind color colour filter',
    'license': 'MIT',
    'packages': ['colourvalgrind'],
    'install_requires': [
        'colorama',
        'regex',
        'six',
        ],
    'entry_points': {
        'console_scripts': ['colour-valgrind=colourvalgrind.command_line:main'],
        },
    'include_package_data': True,
}

setup(**config)
