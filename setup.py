import sys
import os
import pkgutil
import subprocess

from setuptools import setup
from setuptools.command.test import test as TestCommand
from distutils.extension import Extension
from pip.req import parse_requirements

args = sys.argv[2:]
sys.argv = sys.argv[:2]

# Set up handlers for setup.py commands

cmdclass = {}

try:
    import sphinx.setup_command
    class BuildDoc(sphinx.setup_command.BuildDoc):
        def __init__(self, *args, **kwargs):
            # TODO: Do programmatically
            subprocess.call(["sphinx-apidoc", "-o", "doc/api", "."])
            super(BuildDoc, self).__init__(*args, **kwargs)
    cmdclass["doc"] = BuildDoc
except ImportError:
    pass

try:
    from Cython.Distutils import build_ext
    from Cython.Build import cythonize

    cmdclass["build_ext"] = build_ext
except ImportError:
    pass

class Test(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = args
        self.test_suite = True
    
    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        raise SystemExit(errno)

cmdclass["test"] = Test

# Find scripts and requirements

scripts = [os.path.abspath("script/" + p) \
           for p in os.listdir("script/") if os.path.isfile(p) and p != ".gitignore"]

requirements = [str(item.req) for item in 
        parse_requirements("requirements.txt")]

###################
# Extension modules
###################

extensions = [
    Extension("BioTK.genome.region", 
        ["BioTK/genome/region.pyx"]),
    Extension("BioTK.text.types",
        ["BioTK/text/types.pyx"]),
    Extension("BioTK.text.AhoCorasick",
        ["BioTK/text/AhoCorasick.pyx"])
]

class LibraryNotFound(Exception):
    pass

def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs', 
                '-L': 'library_dirs', 
                '-l': 'libraries'}
    try:
        args = ["pkg-config", "--libs", "--cflags"]
        args.extend(packages)
        out = subprocess.check_output(args).decode(sys.getdefaultencoding())
    except subprocess.CalledProcessError:
        raise LibraryNotFound()

    kw = {}
    for token in out.split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
    return kw

# Optional extensions

try:
    libmdb = pkgconfig("libmdb")
    extensions.append(Extension("BioTK.io.MDB", 
        ["BioTK/io/MDB.pyx"], **libmdb))
except LibraryNotFound:
    print("WARNING: libmdb not found. Continuing without BioTK.io.MDB...",
        file=sys.stderr)
 
#####################
# Package description
#####################

setup(
    name="BioTK",
    author="Cory Giles",
    author_email="mail@corygil.es",
    version="0.0.1",
    description="Utilities for genome analysis, expression analysis, and text mining.",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
    license="AGPLv3+",

    # Modules, data, extensions, and scripts to be installed
    packages=["BioTK", "BioTK.io", "BioTK.io.GEO", 
        "BioTK.genome", "BioTK.expression", "BioTK.text"],
    install_requires=requirements,
    tests_require=requirements + ["pytest"],
    extras_require={
        "doc": requirements,
        "mdb": ["mdbread"],
    },
    scripts=scripts,
    ext_modules=extensions,
    #entry_points={
    #    "console_scripts":
    #    ["expression-db-add-family = \
    #            BioTK.expression.meta_analysis:add_family"]
    #}

    # setup.py entry points
    cmdclass=cmdclass
)
