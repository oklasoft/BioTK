=================
How to contribute
=================

If you'd like to contribute to BioTK (yay!), please follow the guidelines
below. In summary:

1. Write the code
2. Write documentation
3. Write tests (that pass)
4. Submit a pull request on GitHub

Although we use PEP8 for variable names and Numpy docstring format (with a few
exceptions), don't obsess over following every detail of these format guides,
especially if you are new to them. Just do what you can, and we can fix minor
errors later.

Writing code
============

Naming conventions
------------------

Code mostly follows standard Python naming conventions from PEP8
(lower_case_with_underscore for variables and functions, CamelCase for classes,
private variables or methods with leading underscore, etc.). 

**There is one exception**: modules and packages. Because of the huge
preponderance of acronyms in biomedicine, modules are CamelCase with acronyms
all uppercase if they describe a file format, external program, or well-known
algorithm. Otherwise, they are lower-case.

Examples:

- BioTK.io.BEDGraph
- BioTK.io.Aspera
- BioTK.text.parse
- BioTK.text.AhoCorasick

Documentation
=============

If you want to contribute some code, the most important kind of documentation
to provide is docstrings. Sphinx documentation and in-code comments are nice
to have, but not crucial.

Sphinx documentation
--------------------

High level information and tutorials are written in the doc/ directory in
reStructuredText format, and built into HTML and other formats using Sphinx.
These docs are automatically mirrored to http://BioTK.readthedocs.org/ .

A useful reStructuredText primer can be found at
http://docutils.sourceforge.net/docs/user/rst/quickref.html .

Docstrings
----------

Modules, and public classes and functions inside them, need docstrings. Keep
it high level, explaining *what* the module/function and the parameters are
doing, not *how* they are doing it. Provide citations to the algorithm's paper
if appropriate. Generally speaking, the more "public" a function/class is, the
more documentation it needs. If it should be rarely or never directly called
by a user, it may only need one line. Conversely, a large class with many
methods may need quite extensive documentation.

The docstrings are written in Numpy format, with one exception: in BioTK,
there is always a leading newline on the first line. Thus, instead of:

.. code-block:: python

    def add(a, b):
        """The sum of two numbers.

        (rest of docstring ...)
        """

we use:

.. code-block:: python

    def add(a, b):
        """
        The sum of two numbers.

        (rest of docstring ...)
        """

The numpy docstring format is described here:

- https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

And many good examples are here:

- http://sphinx-doc.org/latest/ext/example_numpy.html

Internal code comments
----------------------

Functions and class methods should be short enough, and the code should be
clear enough, that code comments should mostly be unnecessary. Use good
judgment: if a particularly tricky method is being used, it may need some
explanation, but in general keep comments high level.

You can mark "wishlist" items with a TODO comment, and items that are actually
broken or need urgent attention with "FIXME" (obviously the latter should be
done sparingly).

Unit tests
==========

They are written using the py.test framework, and are placed in the test/
directory, with a directory structure that mirrors the structure of BioTK.

If possible, avoid tests that take a long time to run or require network
access.
