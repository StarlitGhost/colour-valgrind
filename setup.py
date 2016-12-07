try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Wraps Valgrind to colour the output.',
    'author': 'Matthew Cox',
    'url': 'http://github.com/MatthewCox/colour-valgrind',
    'download_url': '<download url>',
    'author_email': 'matthewcpcox@gmail.com',
    'version': '0.1',
    'install_requires': ['nose', 'colorama'],
    'packages': ['colour-valgrind'],
    'scripts': [],
    'name': 'colour-valgrind'
}

setup(**config)

