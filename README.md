A python wrapper for Valgrind that colours the output for better readability.

Available on pypi here https://pypi.python.org/pypi/colour-valgrind/

Installation
------------

```
pip install colour-valgrind
```

or from the root dir (after cloning):
```
pip install -e .
```

Usage
-----

Just use `colour-valgrind` instead of `valgrind` - all args are passed through.

`--test FILE` has been added to feed in an existing valgrind log file to colour.

Usage as a lib
--------------

You can also use the filter as a library function, if you're running valgrind
from another python project.

```
from colourvalgrind import colour_valgrind

...

print(colour_valgrind(valgrind_output))
```

