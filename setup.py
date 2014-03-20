import os
import pkgutil
import shutil
import subprocess
import sys

from setuptools import setup, find_packages, Extension, Command
from setuptools.command.test import test as TestCommand
from pip.req import parse_requirements

import numpy

args = sys.argv[2:]

################################
# setup.py commands/entry points
################################

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

class Clean(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        base = os.path.abspath(os.path.dirname(__file__))
        dirs = ["BioTK.egg-info", "build", "dist"]
        exts = [".pyc",".so",".o",".pyo",".pyd",".c",".cpp"]

        for dir in dirs:
            path = os.path.join(base, dir)
            if os.path.exists(path):
                print("* recursively removing", path)
                shutil.rmtree(path)

        for root, dirs, files in os.walk(base):
            for f in files:
                if os.path.splitext(f)[-1] in exts:
                    path = os.path.join(root, f)
                    print("* removing", path)
                    os.unlink(path)

cmdclass["clean"] = Clean

###############################
# Find scripts and requirements
###############################

scripts = [os.path.abspath("script/" + p) \
           for p in os.listdir("script/") if os.path.isfile(p) and p != ".gitignore"]

requirements = [str(item.req) for item in 
        parse_requirements("requirements.txt")]

###################
# Extension modules
###################

extensions = [
    Extension("BioTK.genome.region",
        sources=["BioTK/genome/region.pxd", "BioTK/genome/region.pyx"]),
    Extension("BioTK.genome.index",
        sources=["BioTK/genome/index.pyx"]),
    Extension("BioTK.text.types",
        sources=["BioTK/text/types.pyx"]),
    Extension("BioTK.text.AhoCorasick",
        sources=["BioTK/text/AhoCorasick.pyx"])
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

###############################
# Dynamically determine version
###############################

git_dir = os.path.join(os.path.dirname(__file__), ".git")
if os.path.exists(git_dir):
    VERSION = subprocess.check_output(["git", "describe", "--tags"]).strip()\
            .decode("utf-8")
    version_py = os.path.join(os.path.dirname(__file__), "BioTK", "version.py")
    with open(version_py, "w") as handle:
        handle.write("""version = '%s'""" % VERSION)
else:
    VERSION = "HEAD"

#####################
# Package description
#####################

setup(
    name="BioTK",
    author="Cory Giles",
    author_email="mail@corygil.es",
    version=VERSION,
    description="Utilities for genome analysis, expression analysis, and text mining.",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
    license="AGPLv3+",

    # Modules, data, extensions, and scripts to be installed
    packages=find_packages(),
    install_requires=requirements,
    include_dirs=[numpy.get_include()],
    tests_require=requirements + ["pytest"],
    extras_require={
        "doc": requirements,
        "mdb": ["mdbread"],
    },
    scripts=scripts,
    ext_modules=extensions,
    entry_points={
        "console_scripts":
        ["expression-db = BioTK.expression.meta_analysis:main"]
    },

    # setup.py entry points
    cmdclass=cmdclass
)
