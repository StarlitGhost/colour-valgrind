try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readme():
    with open('README.md') as f:
        return f.read()

config = {
    'name': 'colour-valgrind',
    'version': '0.3.2',
    'description': 'Wraps Valgrind to colour the output.',
    'long_description': readme(),
    'author': 'Matthew Cox',
    'url': 'http://github.com/MatthewCox/colour-valgrind',
    'author_email': 'matthewcpcox@gmail.com',
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
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
        ],
    'entry_points': {
        'console_scripts': ['colour-valgrind=colourvalgrind.command_line:main'],
        },
    'include_package_data': True,
}

setup(**config)
